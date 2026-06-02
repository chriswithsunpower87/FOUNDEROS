"""
File: app/agents/risk_analysis_agent.py
Purpose: Agent 10 — performs comprehensive risk analysis on the startup idea.
Responsibilities:
  - Identify business, technical, and market risks
  - Provide mitigation strategies for each risk
  - Final agent — reads from ALL prior agent outputs
Dependencies:
  - app.agents.base_agent (BaseAgent)
"""

import json
from app.agents.base_agent import BaseAgent
from app.agents.state import PipelineState
from app.models.report import AgentType


class RiskAnalysisAgent(BaseAgent):
    """
    Description: Risk Analysis agent — the final specialist in the pipeline.
    Responsibilities:
      - Synthesize all prior analysis to identify risks
      - Provide prioritized risk register with mitigations
    """

    agent_type = AgentType.RISK_ANALYSIS
    agent_name = "Risk Analysis Agent"

    def build_prompt(self, state: PipelineState) -> str:
        # Gather context from all prior agents
        market_size = ""
        if state.get("market_research"):
            market_size = state["market_research"].get("market_size", "")

        competitors = []
        if state.get("competitor_analysis"):
            competitors = [c.get("name", "") for c in state["competitor_analysis"].get("competitors", [])]

        arch_type = ""
        if state.get("technical_architect"):
            arch_type = state["technical_architect"].get("architecture_type", "")

        weeks = 8
        if state.get("roadmap"):
            weeks = state["roadmap"].get("mvp_duration_weeks", 8)

        return f"""You are a Startup Risk Advisor and former VC partner who has evaluated 500+ startups.
You perform rigorous risk analysis across business, technical, market, and execution dimensions.

STARTUP IDEA:
Title: {state['idea_title']}
Problem: {state['problem_statement']}
Target Audience: {state['target_audience']}

CONTEXT:
- Market Size: {market_size}
- Competitors: {', '.join(competitors[:4]) if competitors else 'Unknown'}
- Architecture: {arch_type}
- MVP Timeline: {weeks} weeks

TASK:
Perform a comprehensive risk analysis. Be honest and thorough — identify real failure modes.

Respond ONLY with valid JSON:
{{
  "risks": [
    {{
      "title": "Short risk title",
      "description": "Detailed description of the risk",
      "severity": "HIGH",
      "mitigation": "Specific, actionable mitigation strategy"
    }}
  ],
  "key_assumptions": [
    "Assumption 1 the business is built on",
    "Assumption 2"
  ],
  "failure_points": [
    "The most likely reason this startup fails",
    "Second most likely failure mode"
  ],
  "overall_risk_level": "HIGH | MEDIUM | LOW — with brief justification"
}}

Severity must be exactly HIGH, MEDIUM, or LOW.
Include 5-8 risks covering: market adoption, competition, technical, regulatory, financial."""

    def parse_output(self, raw_response: str) -> dict:
        cleaned = self._clean_json_response(raw_response)
        data = json.loads(cleaned)
        required = ["risks", "key_assumptions", "failure_points", "overall_risk_level"]
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Validate severity values
        valid_severities = {"HIGH", "MEDIUM", "LOW"}
        for risk in data.get("risks", []):
            if risk.get("severity") not in valid_severities:
                risk["severity"] = "MEDIUM"

        return data
