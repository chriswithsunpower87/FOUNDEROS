"""
File: app/agents/competitor_analysis_agent.py
Purpose: Agent 2 — maps the competitive landscape for the startup idea.
Responsibilities:
  - Identify existing competitors with strengths and weaknesses
  - Surface market gaps and differentiation opportunities
Dependencies:
  - app.agents.base_agent (BaseAgent)
"""

import json
from app.agents.base_agent import BaseAgent
from app.agents.state import PipelineState
from app.models.report import AgentType


class CompetitorAnalysisAgent(BaseAgent):
    """
    Description: Performs competitive intelligence analysis for a startup idea.
    Responsibilities:
      - Identify 3-5 real or representative competitors
      - Analyze competitive gaps and positioning opportunities
    """

    agent_type = AgentType.COMPETITOR_ANALYSIS
    agent_name = "Competitor Analysis Agent"

    def build_prompt(self, state: PipelineState) -> str:
        return f"""You are a Competitive Intelligence Analyst who advises top-tier VCs and startups.
You are skilled at mapping competitive landscapes and identifying white space.

STARTUP KNOWLEDGE CONTEXT:
{state.get('rag_context', '')}

STARTUP IDEA:
Title: {state['idea_title']}
Problem: {state['problem_statement']}
Target Audience: {state['target_audience']}

TASK:
Identify competitors and analyze the competitive landscape. Be specific and realistic.

Respond ONLY with valid JSON:
{{
  "competitors": [
    {{
      "name": "Competitor company name",
      "description": "What they do and their market position",
      "strengths": ["strength 1", "strength 2"],
      "weaknesses": ["weakness 1", "weakness 2"]
    }}
  ],
  "market_gaps": ["gap 1", "gap 2", "gap 3"],
  "differentiation_opportunities": ["opportunity 1", "opportunity 2", "opportunity 3"]
}}

Include 3-5 competitors. Be realistic — use real company names if they exist."""

    def parse_output(self, raw_response: str) -> dict:
        cleaned = self._clean_json_response(raw_response)
        data = json.loads(cleaned)
        required = ["competitors", "market_gaps", "differentiation_opportunities"]
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        return data
