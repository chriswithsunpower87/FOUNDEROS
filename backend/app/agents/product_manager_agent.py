"""
File: app/agents/product_manager_agent.py
Purpose: Agent 3 — generates the Product Requirements Document (PRD).
Responsibilities:
  - Define product vision and core features
  - Generate user stories with acceptance criteria
  - Reads from Market Research and Competitor Analysis outputs
Dependencies:
  - app.agents.base_agent (BaseAgent)
"""

import json
from app.agents.base_agent import BaseAgent
from app.agents.state import PipelineState
from app.models.report import AgentType


class ProductManagerAgent(BaseAgent):
    """
    Description: Senior Product Manager agent that generates a PRD.
    Responsibilities:
      - Synthesize market + competitor data into a product vision
      - Define prioritized features and user stories
    """

    agent_type = AgentType.PRODUCT_MANAGER
    agent_name = "Product Manager Agent"

    def build_prompt(self, state: PipelineState) -> str:
        market_context = ""
        if state.get("market_research"):
            mr = state["market_research"]
            market_context = f"Market Size: {mr.get('market_size', 'N/A')}\nKey Trends: {', '.join(mr.get('market_trends', []))}"

        competitor_context = ""
        if state.get("competitor_analysis"):
            ca = state["competitor_analysis"]
            gaps = ca.get("market_gaps", [])
            competitor_context = f"Market Gaps to exploit: {', '.join(gaps)}"

        return f"""You are a Senior Product Manager who has launched products at Stripe, Notion, and Linear.
You write precise, actionable Product Requirements Documents.

STARTUP KNOWLEDGE CONTEXT:
{state.get('rag_context', '')}

STARTUP IDEA:
Title: {state['idea_title']}
Problem: {state['problem_statement']}
Target Audience: {state['target_audience']}

MARKET INSIGHTS:
{market_context}

COMPETITIVE INSIGHTS:
{competitor_context}

TASK:
Write a concise PRD for this product's MVP. Be specific and actionable.

Respond ONLY with valid JSON:
{{
  "product_vision": "1-2 sentence product vision statement",
  "core_features": ["feature 1", "feature 2", "feature 3", "feature 4", "feature 5"],
  "user_stories": [
    {{
      "role": "As a [user type]",
      "action": "I want to [action]",
      "benefit": "so that [benefit]",
      "acceptance_criteria": ["criterion 1", "criterion 2"]
    }}
  ],
  "prd_summary": "2-3 paragraph PRD summary covering vision, scope, and success metrics"
}}

Include 5-7 user stories covering the core features."""

    def parse_output(self, raw_response: str) -> dict:
        cleaned = self._clean_json_response(raw_response)
        data = json.loads(cleaned)
        required = ["product_vision", "core_features", "user_stories", "prd_summary"]
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        return data
