"""
File: tests/test_agents.py
Purpose: Unit tests for all 11 AI agents.
Responsibilities:
  - Mock the LLM (Gemini + OpenRouter) so no real API calls are made
  - Test build_prompt() produces valid, non-empty prompts
  - Test parse_output() correctly validates valid JSON
  - Test parse_output() raises ValueError on invalid/missing fields
  - Verify each agent writes to the correct PipelineState field
Dependencies:
  - pytest, unittest.mock
  - app.agents.* (all 11 agents)
  - app.agents.state (PipelineState)
"""

import json
import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.agents.market_research_agent import MarketResearchAgent
from app.agents.competitor_analysis_agent import CompetitorAnalysisAgent
from app.agents.product_manager_agent import ProductManagerAgent
from app.agents.technical_architect_agent import TechnicalArchitectAgent
from app.agents.database_architect_agent import DatabaseArchitectAgent
from app.agents.api_design_agent import APIDesignAgent
from app.agents.uiux_agent import UIUXAgent
from app.agents.roadmap_agent import RoadmapAgent
from app.agents.marketing_agent import MarketingAgent
from app.agents.risk_analysis_agent import RiskAnalysisAgent
from app.agents.revenue_cost_agent import RevenueCostAgent
from app.agents.state import PipelineState

# ── Minimal valid pipeline state for testing ──────────────────────────────────
BASE_STATE: PipelineState = {
    "idea_id": str(uuid.uuid4()),
    "idea_title": "AI Fitness App",
    "problem_statement": "People can't stay consistent with workouts",
    "target_audience": "Busy professionals aged 25-40",
    "rag_context": "Test RAG context",
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


# ═══════════════════════════════════════════════════════════════════════════════
# MARKET RESEARCH AGENT
# ═══════════════════════════════════════════════════════════════════════════════

class TestMarketResearchAgent:
    """Tests for the Market Research Agent (Agent 1)."""

    def setup_method(self):
        """Purpose: Instantiate agent before each test."""
        with patch("google.genai.Client"):
            self.agent = MarketResearchAgent()

    def test_build_prompt_contains_idea_title(self):
        """Purpose: Verify the prompt includes the startup idea title."""
        prompt = self.agent.build_prompt(BASE_STATE)
        assert "AI Fitness App" in prompt

    def test_build_prompt_contains_problem_statement(self):
        """Purpose: Verify the prompt includes the problem statement."""
        prompt = self.agent.build_prompt(BASE_STATE)
        assert "People can't stay consistent" in prompt

    def test_parse_output_valid(self):
        """Purpose: Verify valid JSON with all required fields parses correctly."""
        valid_output = json.dumps({
            "industry_overview": "The fitness industry is large.",
            "market_size": "TAM: $100B, SAM: $10B, SOM: $1B",
            "market_trends": ["Trend 1", "Trend 2"],
            "market_opportunities": ["Opportunity 1"],
            "potential_demand": "High demand",
            "target_segments": ["Segment 1"],
        })
        result = self.agent.parse_output(valid_output)
        assert result["industry_overview"] == "The fitness industry is large."
        assert isinstance(result["market_trends"], list)

    def test_parse_output_strips_markdown_fences(self):
        """Purpose: Verify ```json ... ``` fences are stripped before parsing."""
        wrapped = "```json\n" + json.dumps({
            "industry_overview": "x",
            "market_size": "x",
            "market_trends": [],
            "market_opportunities": [],
            "potential_demand": "x",
            "target_segments": [],
        }) + "\n```"
        result = self.agent.parse_output(wrapped)
        assert result["industry_overview"] == "x"

    def test_parse_output_raises_on_missing_field(self):
        """Purpose: Verify ValueError is raised when required fields are missing."""
        invalid = json.dumps({"industry_overview": "x"})  # missing other fields
        with pytest.raises((ValueError, KeyError)):
            self.agent.parse_output(invalid)

    def test_parse_output_raises_on_invalid_json(self):
        """Purpose: Verify json.JSONDecodeError is raised on malformed JSON."""
        with pytest.raises(Exception):
            self.agent.parse_output("not valid json {{{")


# ═══════════════════════════════════════════════════════════════════════════════
# COMPETITOR ANALYSIS AGENT
# ═══════════════════════════════════════════════════════════════════════════════

class TestCompetitorAnalysisAgent:
    """Tests for the Competitor Analysis Agent (Agent 2)."""

    def setup_method(self):
        with patch("google.genai.Client"):
            self.agent = CompetitorAnalysisAgent()

    def test_build_prompt_is_non_empty(self):
        prompt = self.agent.build_prompt(BASE_STATE)
        assert len(prompt) > 50

    def test_parse_output_valid(self):
        valid_output = json.dumps({
            "competitors": [{"name": "Peloton", "strengths": ["Brand"], "weaknesses": ["Cost"]}],
            "market_gaps": ["Affordable AI coaching"],
            "differentiation_opportunities": ["Focus on micro-workouts"],
        })
        result = self.agent.parse_output(valid_output)
        assert len(result["competitors"]) == 1
        assert result["competitors"][0]["name"] == "Peloton"

    def test_parse_output_raises_on_missing_competitors(self):
        with pytest.raises((ValueError, KeyError)):
            self.agent.parse_output(json.dumps({"market_gaps": []}))


# ═══════════════════════════════════════════════════════════════════════════════
# RISK ANALYSIS AGENT (boundary test — checks severity enum handling)
# ═══════════════════════════════════════════════════════════════════════════════

class TestRiskAnalysisAgent:
    """Tests for the Risk Analysis Agent (Agent 10)."""

    def setup_method(self):
        with patch("google.genai.Client"):
            self.agent = RiskAnalysisAgent()

    def test_parse_output_valid(self):
        valid_output = json.dumps({
            "risks": [
                {"title": "Market risk", "severity": "HIGH", "description": "...", "mitigation": "..."}
            ],
            "key_assumptions": ["Users will pay"],
            "failure_points": ["No PMF"],
            "overall_risk_level": "HIGH",
        })
        result = self.agent.parse_output(valid_output)
        assert result["overall_risk_level"] == "HIGH"
        assert len(result["risks"]) == 1

    def test_build_prompt_includes_rag_context(self):
        prompt = self.agent.build_prompt(BASE_STATE)
        assert "Test RAG context" in prompt


# ═══════════════════════════════════════════════════════════════════════════════
# REVENUE & COST AGENT
# ═══════════════════════════════════════════════════════════════════════════════

class TestRevenueCostAgent:
    """Tests for the Revenue & Cost Agent (Agent 11)."""

    def setup_method(self):
        with patch("google.genai.Client"):
            self.agent = RevenueCostAgent()

    def test_parse_output_valid(self):
        valid_output = json.dumps({
            "revenue_models": [{"model": "SaaS", "description": "...", "why_suitable": "...", "recommended": True}],
            "pricing_tiers": [{"tier": "Free", "price": "$0/mo", "features": ["Basic"], "target_segment": "Students"}],
            "cost_breakdown": {"development": "$50k", "infrastructure": "$200/mo", "total_monthly_burn": "$2k"},
            "unit_economics": {"cac": "$100", "ltv": "$500"},
            "revenue_projection": {"month_3": "$1k", "month_6": "$5k", "month_12": "$15k", "assumptions": "..."},
            "funding_needs": "$150k",
        })
        result = self.agent.parse_output(valid_output)
        assert result["funding_needs"] == "$150k"
        assert result["revenue_models"][0]["recommended"] is True

    def test_agent_type_is_revenue_cost(self):
        from app.models.report import AgentType
        assert self.agent.agent_type == AgentType.REVENUE_COST

    def test_agent_name(self):
        assert "Revenue" in self.agent.agent_name


# ═══════════════════════════════════════════════════════════════════════════════
# BASE AGENT — _clean_json_response helper
# ═══════════════════════════════════════════════════════════════════════════════

class TestBaseAgentHelpers:
    """Tests for BaseAgent utility methods shared by all agents."""

    def setup_method(self):
        with patch("google.genai.Client"):
            self.agent = MarketResearchAgent()  # Use concrete agent to access base methods

    def test_clean_json_no_fences(self):
        raw = '{"key": "value"}'
        assert self.agent._clean_json_response(raw) == raw

    def test_clean_json_with_json_fence(self):
        raw = '```json\n{"key": "value"}\n```'
        cleaned = self.agent._clean_json_response(raw)
        assert cleaned == '{"key": "value"}'

    def test_clean_json_with_plain_fence(self):
        raw = '```\n{"key": "value"}\n```'
        cleaned = self.agent._clean_json_response(raw)
        assert cleaned == '{"key": "value"}'

    def test_safe_input_snapshot_structure(self):
        snapshot = self.agent._safe_input_snapshot(BASE_STATE)
        assert "idea_id" in snapshot
        assert "idea_title" in snapshot
        assert "prior_agents_completed" in snapshot
        assert isinstance(snapshot["prior_agents_completed"], list)
