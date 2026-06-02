"""
File: app/agents/uiux_agent.py
Purpose: Agent 7 — designs the UI/UX structure and user flows.
Responsibilities:
  - Define screen descriptions, component hierarchies, and user flows
  - Read from Product Manager output
Dependencies:
  - app.agents.base_agent (BaseAgent)
"""

import json
from app.agents.base_agent import BaseAgent
from app.agents.state import PipelineState
from app.models.report import AgentType


class UIUXAgent(BaseAgent):
    """
    Description: UI/UX Design agent that maps the user experience.
    Responsibilities:
      - Define all key screens and their components
      - Map the primary user flow through the product
    """

    agent_type = AgentType.UIUX
    agent_name = "UI/UX Agent"

    def build_prompt(self, state: PipelineState) -> str:
        features = []
        if state.get("product_manager"):
            features = state["product_manager"].get("core_features", [])
            vision = state["product_manager"].get("product_vision", "")
        else:
            vision = ""

        return f"""You are a Senior Product Designer with experience at Figma, Linear, and Notion.
You design clean, user-centric interfaces with clear information architecture.

STARTUP IDEA:
Title: {state['idea_title']}
Problem: {state['problem_statement']}
Target Audience: {state['target_audience']}

PRODUCT VISION: {vision}

CORE FEATURES:
{chr(10).join(f"- {f}" for f in features[:6])}

TASK:
Design the UI/UX structure for this product's MVP.

Respond ONLY with valid JSON:
{{
  "screens": [
    {{
      "name": "Screen Name (e.g. Dashboard, Login)",
      "description": "What this screen does and key elements",
      "components": ["ComponentName", "ComponentName2", "ComponentName3"],
      "user_flow": "How the user arrives here and what they do next"
    }}
  ],
  "design_principles": ["principle 1", "principle 2", "principle 3"],
  "color_scheme": "Recommended colors and rationale (e.g. 'Navy + White — trust and clarity')",
  "typography": "Font recommendations and hierarchy"
}}

Include 6-8 key screens covering the complete user journey."""

    def parse_output(self, raw_response: str) -> dict:
        cleaned = self._clean_json_response(raw_response)
        data = json.loads(cleaned)
        required = ["screens", "design_principles", "color_scheme", "typography"]
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        return data
