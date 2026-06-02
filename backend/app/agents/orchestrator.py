"""
File: app/agents/orchestrator.py
Purpose: Builds and executes the LangGraph agent pipeline.
Responsibilities:
  - Construct the LangGraph StateGraph with all 10 agent nodes
  - Define edges (execution order with parallelism where possible)
  - Compile and execute the graph
  - Update idea status in DB before and after pipeline runs
  - Called as a background task from the /analyze endpoint
Dependencies:
  - langgraph (StateGraph, START, END)
  - app.agents.* (all 10 agent classes)
  - app.agents.state (PipelineState)
  - app.rag.retriever (retrieve_context)
  - app.core.database (get_sync_db)
"""

import uuid
from sqlalchemy import select

from langgraph.graph import END, START, StateGraph

from app.agents.api_design_agent import APIDesignAgent
from app.agents.competitor_analysis_agent import CompetitorAnalysisAgent
from app.agents.database_architect_agent import DatabaseArchitectAgent
from app.agents.market_research_agent import MarketResearchAgent
from app.agents.marketing_agent import MarketingAgent
from app.agents.product_manager_agent import ProductManagerAgent
from app.agents.risk_analysis_agent import RiskAnalysisAgent
from app.agents.roadmap_agent import RoadmapAgent
from app.agents.state import PipelineState
from app.agents.technical_architect_agent import TechnicalArchitectAgent
from app.agents.uiux_agent import UIUXAgent
from app.core.database import get_sync_db
from app.models.idea import Idea, IdeaStatus


def build_pipeline_graph() -> object:
    """
    Purpose: Construct and compile the LangGraph agent pipeline graph.
    Returns:
      CompiledGraph: Ready-to-invoke LangGraph graph.

    Graph execution order:
      [START]
        ├── market_research (Agent 1)   ─┐
        └── competitor_analysis (Agent 2)┘
                ↓ (both complete)
          product_manager (Agent 3)
                ↓
        ├── technical_architect (Agent 4)
        ├── uiux (Agent 7)
        └── marketing (Agent 9)
              ↓ technical_architect completes
        ├── database_architect (Agent 5)
        └── api_design (Agent 6)
              ↓ all above complete
          roadmap (Agent 8)
              ↓
          risk_analysis (Agent 10)
              ↓
            [END]
    """
    builder = StateGraph(PipelineState)

    # ── Register all agent nodes ───────────────────────────────────────────────
    # Note: node names use "run_" prefix to avoid conflict with PipelineState keys
    builder.add_node("run_market_research",     MarketResearchAgent().run)
    builder.add_node("run_competitor_analysis", CompetitorAnalysisAgent().run)
    builder.add_node("run_product_manager",     ProductManagerAgent().run)
    builder.add_node("run_technical_architect", TechnicalArchitectAgent().run)
    builder.add_node("run_database_architect",  DatabaseArchitectAgent().run)
    builder.add_node("run_api_design",          APIDesignAgent().run)
    builder.add_node("run_uiux",                UIUXAgent().run)
    builder.add_node("run_roadmap",             RoadmapAgent().run)
    builder.add_node("run_marketing",           MarketingAgent().run)
    builder.add_node("run_risk_analysis",       RiskAnalysisAgent().run)

    # ── Define execution edges (sequential — avoids concurrent state conflicts) ──
    builder.add_edge(START,                     "run_market_research")
    builder.add_edge("run_market_research",     "run_competitor_analysis")
    builder.add_edge("run_competitor_analysis", "run_product_manager")
    builder.add_edge("run_product_manager",     "run_technical_architect")
    builder.add_edge("run_technical_architect", "run_database_architect")
    builder.add_edge("run_database_architect",  "run_api_design")
    builder.add_edge("run_api_design",          "run_uiux")
    builder.add_edge("run_uiux",                "run_roadmap")
    builder.add_edge("run_roadmap",             "run_marketing")
    builder.add_edge("run_marketing",           "run_risk_analysis")
    builder.add_edge("run_risk_analysis",       END)

    return builder.compile()


def run_pipeline_background(
    idea_id: str,
    idea_title: str,
    problem_statement: str,
    target_audience: str,
) -> None:
    """
    Purpose: Entry point for the background task that runs the full agent pipeline.
      This function runs in a background thread (not async context).
      It updates the idea status before/after the pipeline.
    Parameters:
      idea_id: UUID string of the idea being analyzed.
      idea_title: Title of the startup idea.
      problem_statement: The problem the startup solves.
      target_audience: Who the startup serves.
    """
    db = get_sync_db()

    try:
        # Mark idea as PROCESSING
        idea = db.execute(
            select(Idea).where(Idea.id == uuid.UUID(idea_id))
        ).scalar_one()
        idea.status = IdeaStatus.PROCESSING
        db.commit()

        # Retrieve RAG context for this idea
        try:
            from app.rag.retriever import retrieve_context
            rag_context = retrieve_context(f"{idea_title}: {problem_statement}")
        except Exception as e:
            print(f"⚠️  RAG retrieval failed (continuing without context): {e}")
            rag_context = "No additional context available."

        # Build initial pipeline state
        initial_state: PipelineState = {
            "idea_id": idea_id,
            "idea_title": idea_title,
            "problem_statement": problem_statement,
            "target_audience": target_audience,
            "rag_context": rag_context,
            "market_research": None,
            "competitor_analysis": None,
            "product_manager": None,
            "technical_architect": None,
            "database_architect": None,
            "api_design": None,
            "uiux": None,
            "roadmap": None,
            "marketing": None,
            "risk_analysis": None,
            "errors": [],
        }

        # Build and run the LangGraph pipeline
        graph = build_pipeline_graph()
        final_state = graph.invoke(initial_state)

        # Mark idea as COMPLETED or FAILED based on errors
        idea = db.execute(
            select(Idea).where(Idea.id == uuid.UUID(idea_id))
        ).scalar_one()

        if len(final_state.get("errors", [])) == 10:
            # All agents failed
            idea.status = IdeaStatus.FAILED
        else:
            idea.status = IdeaStatus.COMPLETED

        db.commit()
        print(f"✅ Pipeline complete for idea {idea_id}. Errors: {final_state.get('errors', [])}")

    except Exception as exc:
        print(f"❌ Pipeline fatal error for idea {idea_id}: {exc}")
        # Try to mark idea as failed
        try:
            idea = db.execute(
                select(Idea).where(Idea.id == uuid.UUID(idea_id))
            ).scalar_one_or_none()
            if idea:
                idea.status = IdeaStatus.FAILED
                db.commit()
        except Exception:
            pass

    finally:
        db.close()
