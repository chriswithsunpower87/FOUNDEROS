"""
File: app/agents/marketing_agent.py
Purpose: Agent 9 — creates the go-to-market strategy.
Responsibilities:
  - Define ICP, marketing channels, and launch strategy
  - Read from Market Research and Product Manager outputs
Dependencies:
  - app.agents.base_agent (BaseAgent)
"""

import json
from app.agents.base_agent import BaseAgent
from app.agents.state import PipelineState
from app.models.report import AgentType


class MarketingAgent(BaseAgent):
    """
    Description: Growth and Marketing agent that designs the GTM strategy.
    Responsibilities:
      - Define the Ideal Customer Profile (ICP)
      - Recommend channels and launch tactics
    """

    agent_type = AgentType.MARKETING
    agent_name = "Marketing Agent"

    def build_prompt(self, state: PipelineState) -> str:
        segments = []
        if state.get("market_research"):
            segments = state["market_research"].get("target_segments", [])

        gaps = []
        if state.get("competitor_analysis"):
            gaps = state["competitor_analysis"].get("differentiation_opportunities", [])

        return f"""You are a Growth Marketing expert who has launched products at Product Hunt #1 spots.
You specialize in zero-budget, high-impact GTM strategies for early-stage startups.

STARTUP IDEA:
Title: {state['idea_title']}
Problem: {state['problem_statement']}
Target Audience: {state['target_audience']}

TARGET SEGMENTS: {', '.join(segments)}
DIFFERENTIATION: {', '.join(gaps[:3])}

TASK:
Create a go-to-market strategy for the MVP launch.

Respond ONLY with valid JSON:
{{
  "ideal_customer_profile": "Detailed ICP: demographics, psychographics, job title, pain points, where they spend time online",
  "marketing_channels": [
    {{
      "channel": "Channel name (e.g. LinkedIn, Product Hunt, Reddit)",
      "rationale": "Why this channel for this audience",
      "estimated_cost": "Free | Low ($0-100/mo) | Medium ($100-500/mo)"
    }}
  ],
  "launch_strategy": "3-4 sentence description of the launch sequence and approach",
  "growth_tactics": ["tactic 1", "tactic 2", "tactic 3", "tactic 4"]
}}

Include 4-6 marketing channels. Prioritize free and low-cost channels for MVP."""

    def parse_output(self, raw_response: str) -> dict:
        cleaned = self._clean_json_response(raw_response)
        data = json.loads(cleaned)
        required = ["ideal_customer_profile", "marketing_channels", "launch_strategy", "growth_tactics"]
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        return data
