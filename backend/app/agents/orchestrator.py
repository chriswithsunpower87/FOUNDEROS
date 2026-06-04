"""
File: app/agents/orchestrator.py
Purpose: Builds and executes the LangGraph agent pipeline with parallelism.
Responsibilities:
  - Construct a parallel LangGraph StateGraph across all 11 agents
  - Use fan-out/fan-in edges so independent agents run concurrently
  - Compile and execute the graph
  - Update idea status in DB before and after pipeline runs
  - Called as a background task from the /analyze endpoint
Dependencies:
  - langgraph (StateGraph, START, END)
  - app.agents.* (all 11 agent classes)
  - app.agents.state (PipelineState)
  - app.rag.retriever (retrieve_context)
  - app.core.database (get_sync_db)

Parallel Execution DAG:
  ┌─ market_research (1) ─────────────────────────────────────────────┐
  │                                                                     │→ product_manager (3)
  └─ competitor_analysis (2) ─────────────────────────────────────────┘         │
                                                                      ┌──────────┤
                                              technical_architect (4)─┤  marketing (9)
                                                        │             └──────────┤
                                            ┌──────────┤                        │
                                database_architect (5) │ uiux (7)               │
                                            │          │                        │
                                      api_design (6)   │                        │
                                            │          │                        │
                                         roadmap (8) ──┤                        │
                                                       └──── risk_analysis (10) ┘
                                                                    │
                                                          revenue_cost (11)
                                                                    │
                                                                  [END]
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
from app.agents.revenue_cost_agent import RevenueCostAgent
from app.agents.risk_analysis_agent import RiskAnalysisAgent
from app.agents.roadmap_agent import RoadmapAgent
from app.agents.state import PipelineState
from app.agents.technical_architect_agent import TechnicalArchitectAgent
from app.agents.uiux_agent import UIUXAgent
from app.core.database import get_sync_db
from app.models.idea import Idea, IdeaStatus


def build_pipeline_graph() -> object:
    """
    Purpose: Construct and compile the parallel LangGraph agent pipeline.
    Returns:
      CompiledGraph: Ready-to-invoke LangGraph graph with parallel branches.

    Execution phases (independent agents run in parallel within each phase):
      Phase 1 (parallel): market_research || competitor_analysis
      Phase 2 (barrier):  product_manager   ← waits for both Phase 1 nodes
      Phase 3 (parallel): technical_architect || marketing
      Phase 4 (parallel): database_architect || uiux  ← both after technical_architect
      Phase 5 (sequential): api_design → roadmap
      Phase 6 (barrier):  risk_analysis   ← waits for roadmap + uiux + marketing
      Phase 7 (sequential): revenue_cost → END

    LangGraph fan-in semantics: when multiple edges point to the same node,
    that node waits for ALL predecessors to complete before it runs.
    This is the synchronization barrier (join) pattern.
    """
    builder = StateGraph(PipelineState)

    # ── Register all 11 agent nodes ────────────────────────────────────────────
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
    builder.add_node("run_revenue_cost",        RevenueCostAgent().run)

    # ── Phase 1: Fan-out from START → agents 1 and 2 run in parallel ──────────
    builder.add_edge(START, "run_market_research")
    builder.add_edge(START, "run_competitor_analysis")

    # ── Phase 2: Fan-in → product_manager waits for BOTH Phase 1 agents ───────
    builder.add_edge("run_market_research",     "run_product_manager")
    builder.add_edge("run_competitor_analysis", "run_product_manager")

    # ── Phase 3: Fan-out → technical_architect and marketing run in parallel ───
    # marketing only needs product_manager + market_research (already in state)
    builder.add_edge("run_product_manager", "run_technical_architect")
    builder.add_edge("run_product_manager", "run_marketing")

    # ── Phase 4: database_architect and uiux run in parallel ──────────────────
    # both need technical_architect output; neither needs the other
    builder.add_edge("run_technical_architect", "run_database_architect")
    builder.add_edge("run_technical_architect", "run_uiux")

    # ── Phase 5: Technical pipeline finishes sequentially ─────────────────────
    builder.add_edge("run_database_architect", "run_api_design")
    builder.add_edge("run_api_design",         "run_roadmap")

    # ── Phase 6: Fan-in → risk_analysis waits for roadmap + uiux + marketing ──
    builder.add_edge("run_roadmap",   "run_risk_analysis")
    builder.add_edge("run_uiux",      "run_risk_analysis")
    builder.add_edge("run_marketing", "run_risk_analysis")

    # ── Phase 7: Final sequential ─────────────────────────────────────────────
    builder.add_edge("run_risk_analysis", "run_revenue_cost")
    builder.add_edge("run_revenue_cost",  END)

    return builder.compile()


def run_pipeline_background(
    idea_id: str,
    idea_title: str,
    problem_statement: str,
    target_audience: str,
) -> None:
    """
    Purpose: Entry point for the background task that runs the full agent pipeline.
      Runs in a background thread (not async context).
      Updates idea status before/after pipeline execution.
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

        # Retrieve RAG context (enriches every agent's prompt)
        try:
            from app.rag.retriever import retrieve_context
            rag_context = retrieve_context(f"{idea_title}: {problem_statement}")
        except Exception as e:
            print(f"⚠️  RAG retrieval failed (non-fatal): {e}")
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
            "revenue_cost": None,
            "errors": [],
        }

        # Build and execute the parallel LangGraph pipeline
        graph = build_pipeline_graph()
        final_state = graph.invoke(initial_state)

        # Mark idea COMPLETED or FAILED
        idea = db.execute(
            select(Idea).where(Idea.id == uuid.UUID(idea_id))
        ).scalar_one()

        errors = final_state.get("errors", [])
        idea.status = IdeaStatus.FAILED if len(errors) == 11 else IdeaStatus.COMPLETED
        db.commit()

        print(
            f"✅ Pipeline complete [{idea_id}] — "
            f"{11 - len(errors)}/11 agents succeeded. "
            f"Errors: {errors}"
        )

    except Exception as exc:
        print(f"❌ Pipeline fatal error [{idea_id}]: {exc}")
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
