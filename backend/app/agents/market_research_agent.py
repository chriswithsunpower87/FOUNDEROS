"""
File: app/agents/market_research_agent.py
Purpose: Agent 1 — analyzes the market landscape for the startup idea.
Responsibilities:
  - Generate industry overview, market size, trends, and opportunities
  - First agent to run — no prior agent outputs available
Dependencies:
  - app.agents.base_agent (BaseAgent)
  - app.agents.state (PipelineState)
"""

import json
from app.agents.base_agent import BaseAgent
from app.agents.state import PipelineState
from app.models.report import AgentType


class MarketResearchAgent(BaseAgent):
    """
    Description: Specialist agent that performs market research for a startup idea.
    Responsibilities:
      - Analyze industry size, trends, and growth opportunity
      - Identify target market segments and demand signals
    """

    agent_type = AgentType.MARKET_RESEARCH
    agent_name = "Market Research Agent"

    def build_prompt(self, state: PipelineState) -> str:
        """
        Purpose: Construct the market research prompt.
        Parameters:
          state: Pipeline state with idea details and RAG context.
        Returns:
          str: Complete prompt for the LLM.
        """
        return f"""You are a Senior Market Research Analyst with 15 years of experience at McKinsey & Company.
You specialize in technology startup markets and investment due diligence.

STARTUP KNOWLEDGE CONTEXT (use this to inform your analysis):
{state.get('rag_context', '')}

STARTUP IDEA:
Title: {state['idea_title']}
Problem: {state['problem_statement']}
Target Audience: {state['target_audience']}

TASK:
Analyze the market for this startup idea. Think carefully about market size, growth trends, and opportunities.

Respond ONLY with valid JSON matching this exact structure (no markdown, no explanation):
{{
  "industry_overview": "2-3 sentence overview of the industry this startup operates in",
  "market_size": "Estimated TAM/SAM/SOM with reasoning",
  "market_trends": ["trend 1", "trend 2", "trend 3", "trend 4"],
  "market_opportunities": ["opportunity 1", "opportunity 2", "opportunity 3"],
  "potential_demand": "Assessment of demand strength and growth trajectory",
  "target_segments": ["segment 1", "segment 2", "segment 3"]
}}"""

    def parse_output(self, raw_response: str) -> dict:
        """
        Purpose: Parse and validate the LLM market research output.
        Parameters:
          raw_response: Raw JSON string from the LLM.
        Returns:
          dict: Validated market research output.
        """
        cleaned = self._clean_json_response(raw_response)
        data = json.loads(cleaned)

        required = ["industry_overview", "market_size", "market_trends",
                    "market_opportunities", "potential_demand", "target_segments"]
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        return data
