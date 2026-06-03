"""
File: app/agents/base_agent.py
Purpose: Abstract base class that all 10 FounderOS AI agents extend.
Responsibilities:
  - Define the contract (build_prompt, parse_output, run) all agents must implement
  - Call Gemini API as primary LLM with automatic OpenRouter fallback
  - Save every execution as a trace to the agent_runs table
  - Update the report status in the reports table
Dependencies:
  - google.generativeai (Gemini SDK)
  - httpx (OpenRouter HTTP client)
  - app.agents.state (PipelineState)
  - app.services.report_service (sync DB helpers)
  - app.core.config (settings)
"""

import json
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

import httpx
from google import genai

from app.agents.state import PipelineState
from app.core.config import settings
from app.core.database import get_sync_db
from app.models.report import AgentType, ReportStatus
from app.services.report_service import (
    sync_fail_report,
    sync_save_agent_run,
    sync_save_report_output,
    sync_update_report_running,
)


class BaseAgent(ABC):
    """
    Description: Abstract base class for all FounderOS AI specialist agents.
    Responsibilities:
      - Enforce the run() interface used by LangGraph nodes
      - Handle LLM calls with primary (Gemini) and fallback (OpenRouter) models
      - Save trace data and report outputs to PostgreSQL
      - Allow the pipeline to continue even if this agent fails
    """

    # Subclasses must set these class-level attributes
    agent_type: AgentType
    agent_name: str

    def __init__(self):
        """
        Purpose: Initialize Gemini client using the API key from settings.
        Uses the new google-genai SDK which supports both AIzaSy and AQ.A key formats.
        """
        self.gemini_client = genai.Client(api_key=settings.gemini_api_key)

    # ── Abstract interface ─────────────────────────────────────────────────────

    @abstractmethod
    def build_prompt(self, state: PipelineState) -> str:
        """
        Purpose: Build the complete LLM prompt from the current pipeline state.
        Parameters:
          state: The current pipeline state (prior agent outputs available here).
        Returns:
          str: The full prompt string to send to the LLM.
        """
        pass

    @abstractmethod
    def parse_output(self, raw_response: str) -> dict[str, Any]:
        """
        Purpose: Parse and validate the LLM's raw string response.
        Parameters:
          raw_response: The raw text returned by the LLM.
        Returns:
          dict: Structured output matching this agent's schema.
        Raises:
          ValueError: If JSON is invalid or schema validation fails.
        """
        pass

    # ── Main execution method (used as LangGraph node) ────────────────────────

    def run(self, state: PipelineState) -> PipelineState:
        """
        Purpose: Execute this agent and return the updated pipeline state.
          This method is registered as a LangGraph node and called automatically.
        Parameters:
          state: Current pipeline state with all prior agent outputs.
        Returns:
          PipelineState: Updated state with this agent's output field populated.
        Notes:
          - Never raises — errors are caught, logged, and pipeline continues
        """
        idea_id = uuid.UUID(state["idea_id"])
        start_time = datetime.now(timezone.utc)
        start_ms = time.monotonic()
        prompt = ""
        db = get_sync_db()

        try:
            # Mark report as RUNNING in the database
            report = sync_update_report_running(db, idea_id, self.agent_type)

            # Build the LLM prompt
            prompt = self.build_prompt(state)

            # Call LLM (Gemini → OpenRouter fallback)
            model_name, raw_output, tokens_used = self._call_llm_with_fallback(prompt)

            # Parse and validate structured output
            parsed = self.parse_output(raw_output)

            # Calculate execution time
            execution_ms = int((time.monotonic() - start_ms) * 1000)

            # Save output to reports table
            sync_save_report_output(
                db=db,
                idea_id=idea_id,
                agent_type=self.agent_type,
                output=parsed,
                reasoning_summary=f"{self.agent_name} completed analysis in {execution_ms}ms using {model_name}",
                execution_time_ms=execution_ms,
            )

            # Save agent run trace
            sync_save_agent_run(
                db=db,
                report_id=report.id,
                agent_name=self.agent_name,
                input_snapshot=self._safe_input_snapshot(state),
                output_snapshot=parsed,
                prompt_used=prompt,
                model_used=model_name,
                tokens_used=tokens_used,
                status=ReportStatus.COMPLETED,
                error_message=None,
                started_at=start_time,
            )

            # Write output into pipeline state for downstream agents
            return self._update_state(state, parsed)

        except Exception as exc:
            error_msg = f"{self.agent_name} failed: {str(exc)}"
            print(f"❌ {error_msg}")

            sync_fail_report(db, idea_id, self.agent_type, error_msg)

            # Try to save the failed run trace
            try:
                report_result = db.execute(
                    __import__("sqlalchemy").select(
                        __import__("app.models.report", fromlist=["Report"]).Report
                    ).where(
                        __import__("app.models.report", fromlist=["Report"]).Report.idea_id == idea_id,
                        __import__("app.models.report", fromlist=["Report"]).Report.agent_type == self.agent_type,
                    )
                ).scalar_one_or_none()

                if report_result:
                    sync_save_agent_run(
                        db=db,
                        report_id=report_result.id,
                        agent_name=self.agent_name,
                        input_snapshot=self._safe_input_snapshot(state),
                        output_snapshot=None,
                        prompt_used=prompt,
                        model_used="unknown",
                        tokens_used=None,
                        status=ReportStatus.FAILED,
                        error_message=error_msg,
                        started_at=start_time,
                    )
            except Exception:
                pass  # Don't let trace saving break the pipeline

            # Accumulate error — pipeline continues to other agents
            updated_state = dict(state)
            updated_state["errors"] = state.get("errors", []) + [error_msg]
            return updated_state  # type: ignore

        finally:
            db.close()

    # ── LLM calling with fallback ─────────────────────────────────────────────

    # Free models tried in order when Gemini is unavailable.
    # If one returns 404/401/403 we skip to the next automatically.
    OPENROUTER_FALLBACK_MODELS = [
        "mistralai/mistral-7b-instruct:free",
        "meta-llama/llama-3.1-8b-instruct:free",
        "google/gemma-2-9b-it:free",
        "openchat/openchat-7b:free",
        "nousresearch/nous-capybara-7b:free",
    ]

    def _call_llm_with_fallback(
        self, prompt: str
    ) -> tuple[str, str, int | None]:
        """
        Purpose: Attempt Gemini first, then try each OpenRouter free model
          in sequence until one succeeds.
        Parameters:
          prompt: The full LLM prompt string.
        Returns:
          tuple: (model_name, raw_text_response, tokens_used_or_None)
        Raises:
          RuntimeError: If every LLM attempt fails.
        """
        # ── Try Gemini (one attempt, fail fast) ────────────────────────────────
        try:
            response = self.gemini_client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
            )
            tokens = None
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                tokens = response.usage_metadata.total_token_count
            return settings.gemini_model, response.text, tokens

        except Exception as gemini_error:
            print(f"⚠️  Gemini failed ({gemini_error}), trying OpenRouter fallbacks...")

        # ── Try each OpenRouter model in order ─────────────────────────────────
        last_error: Exception | None = None

        with httpx.Client(timeout=120) as client:
            for model in self.OPENROUTER_FALLBACK_MODELS:
                try:
                    print(f"   Trying OpenRouter model: {model}")
                    response = client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {settings.openrouter_api_key}",
                            "Content-Type": "application/json",
                            "HTTP-Referer": "http://localhost:3000",
                            "X-Title": "FounderOS",
                        },
                        json={
                            "model": model,
                            "messages": [{"role": "user", "content": prompt}],
                            "max_tokens": 4096,
                        },
                    )
                    response.raise_for_status()
                    data = response.json()
                    text = data["choices"][0]["message"]["content"]
                    tokens = data.get("usage", {}).get("total_tokens")
                    print(f"   ✅ OpenRouter success with: {model}")
                    return model, text, tokens

                except Exception as e:
                    print(f"   ❌ {model} failed: {e}")
                    last_error = e
                    continue

        raise RuntimeError(
            f"All LLM providers failed. Last error: {last_error}"
        )

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _clean_json_response(self, raw: str) -> str:
        """
        Purpose: Strip markdown code fences that LLMs sometimes wrap JSON in.
        Parameters:
          raw: Raw LLM response string.
        Returns:
          str: Cleaned string ready for json.loads().
        """
        cleaned = raw.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return cleaned.strip()

    def _safe_input_snapshot(self, state: PipelineState) -> dict:
        """
        Purpose: Extract a safe subset of state to store as the input snapshot.
          Truncates rag_context to avoid storing huge blobs.
        Parameters:
          state: Full pipeline state.
        Returns:
          dict: Snapshot suitable for JSON storage in agent_runs.
        """
        return {
            "idea_id": state.get("idea_id"),
            "idea_title": state.get("idea_title"),
            "problem_statement": state.get("problem_statement"),
            "target_audience": state.get("target_audience"),
            "rag_context_length": len(state.get("rag_context", "")),
            "prior_agents_completed": [
                k for k in [
                    "market_research", "competitor_analysis", "product_manager",
                    "technical_architect", "database_architect", "api_design",
                    "uiux", "roadmap", "marketing", "risk_analysis",
                ]
                if state.get(k) is not None
            ],
        }

    def _update_state(self, state: PipelineState, output: dict) -> PipelineState:
        """
        Purpose: Return a new state dict with this agent's output field set.
        Parameters:
          state: Current pipeline state.
          output: This agent's parsed output dict.
        Returns:
          PipelineState: Updated state.
        """
        # Map agent_type to the state field name
        field_map = {
            AgentType.MARKET_RESEARCH: "market_research",
            AgentType.COMPETITOR_ANALYSIS: "competitor_analysis",
            AgentType.PRODUCT_MANAGER: "product_manager",
            AgentType.TECHNICAL_ARCHITECT: "technical_architect",
            AgentType.DATABASE_ARCHITECT: "database_architect",
            AgentType.API_DESIGN: "api_design",
            AgentType.UIUX: "uiux",
            AgentType.ROADMAP: "roadmap",
            AgentType.MARKETING: "marketing",
            AgentType.RISK_ANALYSIS: "risk_analysis",
        }
        field = field_map[self.agent_type]
        updated = dict(state)
        updated[field] = output
        return updated  # type: ignore
