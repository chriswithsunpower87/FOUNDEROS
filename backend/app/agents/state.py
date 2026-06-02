"""
File: app/agents/state.py
Purpose: Defines the shared typed state object passed between all LangGraph agents.
Responsibilities:
  - Declare every field the pipeline state can hold
  - Typed as a TypedDict for LangGraph compatibility
  - Earlier agent outputs become inputs to later agents via this state
Dependencies:
  - typing (TypedDict, Optional, List)
"""

from typing import Any, Optional
from typing_extensions import TypedDict


class PipelineState(TypedDict):
    """
    Description: The shared state object that flows through the entire LangGraph pipeline.
    Responsibilities:
      - Carry idea input data to all agents
      - Accumulate each agent's output as the pipeline progresses
      - Track errors without stopping the pipeline
    Notes:
      - All output fields are Optional — they start as None and are filled as agents complete
      - Each agent reads from prior agents' fields and writes to its own field
    """

    # ── Pipeline inputs (set before the graph starts) ─────────────────────────
    idea_id: str
    idea_title: str
    problem_statement: str
    target_audience: str
    rag_context: str            # Startup methodology context retrieved from ChromaDB

    # ── Agent outputs (filled sequentially as each agent completes) ────────────
    market_research: Optional[dict[str, Any]]
    competitor_analysis: Optional[dict[str, Any]]
    product_manager: Optional[dict[str, Any]]
    technical_architect: Optional[dict[str, Any]]
    database_architect: Optional[dict[str, Any]]
    api_design: Optional[dict[str, Any]]
    uiux: Optional[dict[str, Any]]
    roadmap: Optional[dict[str, Any]]
    marketing: Optional[dict[str, Any]]
    risk_analysis: Optional[dict[str, Any]]

    # ── Error accumulator — failed agents append here, pipeline continues ──────
    errors: list[str]
