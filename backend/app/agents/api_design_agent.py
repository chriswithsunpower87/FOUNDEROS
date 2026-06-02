"""
File: app/agents/api_design_agent.py
Purpose: Agent 6 — designs the REST API for the startup.
Responsibilities:
  - Define endpoints, request/response shapes, and HTTP methods
  - Read from Technical Architect and Product Manager outputs
Dependencies:
  - app.agents.base_agent (BaseAgent)
"""

import json
from app.agents.base_agent import BaseAgent
from app.agents.state import PipelineState
from app.models.report import AgentType


class APIDesignAgent(BaseAgent):
    """
    Description: API Design agent that defines the REST interface.
    Responsibilities:
      - Design RESTful endpoints for core product features
      - Provide request/response examples
    """

    agent_type = AgentType.API_DESIGN
    agent_name = "API Design Agent"

    def build_prompt(self, state: PipelineState) -> str:
        features = []
        if state.get("product_manager"):
            features = state["product_manager"].get("core_features", [])

        return f"""You are a Backend API Architect who has designed APIs used by millions of users.
You write clear, consistent, well-structured REST APIs following industry standards.

STARTUP IDEA:
Title: {state['idea_title']}
Problem: {state['problem_statement']}

CORE FEATURES TO BUILD APIS FOR:
{chr(10).join(f"- {f}" for f in features[:6])}

TASK:
Design the REST API for this startup's MVP. Follow REST conventions.

Respond ONLY with valid JSON:
{{
  "endpoints": [
    {{
      "method": "POST",
      "path": "/api/v1/resource",
      "description": "What this endpoint does",
      "request_example": {{"field": "value"}},
      "response_example": {{"id": "uuid", "field": "value"}}
    }}
  ],
  "design_notes": "API design principles applied, versioning strategy, authentication approach"
}}

Include 8-12 endpoints covering auth, core resources, and key operations.
Use realistic JSON examples."""

    def parse_output(self, raw_response: str) -> dict:
        cleaned = self._clean_json_response(raw_response)
        data = json.loads(cleaned)
        required = ["endpoints", "design_notes"]
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        return data
