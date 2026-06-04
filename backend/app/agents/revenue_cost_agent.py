"""
File: app/agents/revenue_cost_agent.py
Purpose: Agent 11 — generates revenue models and cost estimation for the startup.
Responsibilities:
  - Recommend monetization strategies (subscriptions, freemium, usage-based, etc.)
  - Estimate cost breakdown for building and operating the MVP
  - Suggest pricing tiers with rationale
  - Runs after all 10 primary agents so it can reference the full blueprint
Dependencies:
  - app.agents.base_agent (BaseAgent)
  - app.agents.state (PipelineState)
  - app.models.report (AgentType)
"""

import json
from app.agents.base_agent import BaseAgent
from app.agents.state import PipelineState
from app.models.report import AgentType


class RevenueCostAgent(BaseAgent):
    """
    Description: Specialist agent that designs revenue models and cost structures.
    Responsibilities:
      - Identify the most suitable monetization strategies for the startup
      - Estimate development, infrastructure, and operational costs for MVP
      - Suggest pricing tiers with expected conversion and churn data
      - Provide a 12-month revenue projection scenario
    """

    agent_type = AgentType.REVENUE_COST
    agent_name = "Revenue & Cost Agent"

    def build_prompt(self, state: PipelineState) -> str:
        """
        Purpose: Construct the revenue and cost analysis prompt.
          Uses prior agent outputs (market research, technical architect, roadmap)
          to ground the financial model in reality.
        Parameters:
          state: Pipeline state with all prior agent outputs available.
        Returns:
          str: Complete prompt for the LLM.
        """
        # Pull context from prior agents for a grounded financial model
        market_size     = ""
        architecture    = ""
        roadmap_weeks   = ""
        product_vision  = ""

        if state.get("market_research"):
            market_size = state["market_research"].get("market_size", "")  # type: ignore

        if state.get("technical_architect"):
            architecture = state["technical_architect"].get("high_level_design", "")  # type: ignore

        if state.get("roadmap"):
            roadmap_weeks = str(state["roadmap"].get("mvp_duration_weeks", ""))  # type: ignore

        if state.get("product_manager"):
            product_vision = state["product_manager"].get("product_vision", "")  # type: ignore

        return f"""You are a Senior Financial Analyst and Startup CFO with 15 years of experience
advising early-stage SaaS and consumer tech companies.

STARTUP KNOWLEDGE CONTEXT:
{state.get('rag_context', '')}

STARTUP IDEA:
Title: {state['idea_title']}
Problem: {state['problem_statement']}
Target Audience: {state['target_audience']}

CONTEXT FROM PRIOR AGENTS:
Market Size: {market_size}
Product Vision: {product_vision}
Architecture Type: {architecture}
MVP Duration: {roadmap_weeks} weeks

TASK:
Design a realistic revenue model and cost structure for this startup's MVP phase.
Focus on practical, achievable numbers for a bootstrapped or seed-stage startup.

Respond ONLY with valid JSON matching this exact structure (no markdown, no explanation):
{{
  "revenue_models": [
    {{
      "model": "model name (e.g. Freemium, SaaS Subscription, Usage-Based)",
      "description": "how this model works for this specific startup",
      "why_suitable": "why this fits this startup's audience and problem",
      "recommended": true
    }}
  ],
  "pricing_tiers": [
    {{
      "tier": "Free / Starter / Pro / Enterprise",
      "price": "$0/mo or $X/mo",
      "features": ["feature 1", "feature 2"],
      "target_segment": "who this tier targets"
    }}
  ],
  "cost_breakdown": {{
    "development": "estimated one-time MVP build cost in $",
    "infrastructure": "monthly hosting/cloud cost estimate",
    "ai_api_costs": "monthly LLM/AI API cost estimate",
    "marketing": "estimated monthly marketing spend",
    "operations": "other monthly operational costs",
    "total_monthly_burn": "total estimated monthly burn rate"
  }},
  "unit_economics": {{
    "cac": "estimated Customer Acquisition Cost",
    "ltv": "estimated Customer Lifetime Value",
    "ltv_cac_ratio": "LTV:CAC ratio",
    "payback_period": "estimated months to recover CAC"
  }},
  "revenue_projection": {{
    "month_3": "estimated MRR at 3 months",
    "month_6": "estimated MRR at 6 months",
    "month_12": "estimated MRR at 12 months",
    "assumptions": "key assumptions behind these projections"
  }},
  "funding_needs": "estimate of how much capital is needed to reach profitability"
}}"""

    def parse_output(self, raw_response: str) -> dict:
        """
        Purpose: Parse and validate the revenue and cost analysis output.
        Parameters:
          raw_response: Raw JSON string from the LLM.
        Returns:
          dict: Validated revenue and cost output.
        Raises:
          ValueError: If required fields are missing or JSON is invalid.
        """
        cleaned = self._clean_json_response(raw_response)
        data = json.loads(cleaned)

        required = [
            "revenue_models", "pricing_tiers", "cost_breakdown",
            "unit_economics", "revenue_projection", "funding_needs",
        ]
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        return data
