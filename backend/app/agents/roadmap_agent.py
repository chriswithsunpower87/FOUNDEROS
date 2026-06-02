"""
File: app/agents/roadmap_agent.py
Purpose: Agent 8 — creates the week-by-week MVP development roadmap.
Responsibilities:
  - Generate a realistic 6-8 week MVP development plan
  - Reads from PM, Tech, DB, API, and UI/UX outputs
Dependencies:
  - app.agents.base_agent (BaseAgent)
"""

import json
from app.agents.base_agent import BaseAgent
from app.agents.state import PipelineState
from app.models.report import AgentType


class RoadmapAgent(BaseAgent):
    """
    Description: Roadmap agent that creates a phased MVP development plan.
    Responsibilities:
      - Break MVP into weekly sprints with clear deliverables
      - Sequence work logically (infra → auth → core → polish → launch)
    """

    agent_type = AgentType.ROADMAP
    agent_name = "Roadmap Agent"

    def build_prompt(self, state: PipelineState) -> str:
        features = []
        if state.get("product_manager"):
            features = state["product_manager"].get("core_features", [])

        stack = {}
        if state.get("technical_architect"):
            stack = state["technical_architect"].get("recommended_stack", {})

        return f"""You are a Technical Program Manager who has led 0→1 product launches at YC-backed startups.
You create realistic, achievable development roadmaps for small teams.

STARTUP IDEA:
Title: {state['idea_title']}
Problem: {state['problem_statement']}

CORE FEATURES TO BUILD:
{chr(10).join(f"- {f}" for f in features[:6])}

TECH STACK:
{json.dumps(stack, indent=2)}

TASK:
Create a week-by-week MVP development roadmap for a solo developer or 2-person team.
Be realistic. Include infrastructure setup, core features, and launch prep.

Respond ONLY with valid JSON:
{{
  "mvp_duration_weeks": 8,
  "weeks": [
    {{
      "week": 1,
      "focus": "One-line focus for the week",
      "deliverables": ["deliverable 1", "deliverable 2", "deliverable 3"],
      "milestone": "End-of-week milestone"
    }}
  ],
  "definition_of_done": "What 'MVP complete' means for this product"
}}"""

    def parse_output(self, raw_response: str) -> dict:
        cleaned = self._clean_json_response(raw_response)
        data = json.loads(cleaned)
        required = ["mvp_duration_weeks", "weeks", "definition_of_done"]
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        return data
