"""
File: app/agents/technical_architect_agent.py
Purpose: Agent 4 — designs the technical architecture for the startup.
Responsibilities:
  - Recommend tech stack and architecture pattern
  - Provide scalability and infrastructure guidance
  - Reads from Product Manager output
Dependencies:
  - app.agents.base_agent (BaseAgent)
"""

import json
from app.agents.base_agent import BaseAgent
from app.agents.state import PipelineState
from app.models.report import AgentType


class TechnicalArchitectAgent(BaseAgent):
    """
    Description: Principal Software Architect agent.
    Responsibilities:
      - Design high-level system architecture for the startup's MVP
      - Recommend appropriate tech stack based on product requirements
    """

    agent_type = AgentType.TECHNICAL_ARCHITECT
    agent_name = "Technical Architect Agent"

    def build_prompt(self, state: PipelineState) -> str:
        features_context = ""
        if state.get("product_manager"):
            pm = state["product_manager"]
            features = pm.get("core_features", [])
            features_context = f"Core features to support: {', '.join(features[:5])}"

        return f"""You are a Principal Software Architect with experience at Google, Netflix, and Airbnb.
You design scalable, cost-effective architectures for early-stage startups.

STARTUP KNOWLEDGE CONTEXT:
{state.get('rag_context', '')}

STARTUP IDEA:
Title: {state['idea_title']}
Problem: {state['problem_statement']}
Target Audience: {state['target_audience']}

PRODUCT CONTEXT:
{features_context}

TASK:
Design the technical architecture for this startup's MVP. Prioritize simplicity and cost-effectiveness.

Respond ONLY with valid JSON:
{{
  "architecture_type": "Monolith | Modular Monolith | Microservices — with explanation of why",
  "recommended_stack": {{
    "frontend": "Framework and key libraries",
    "backend": "Framework, language, and runtime",
    "database": "Primary database and why",
    "infrastructure": "Hosting and deployment strategy"
  }},
  "high_level_design": "3-4 sentence description of the overall system design",
  "scalability_notes": ["note 1", "note 2", "note 3"],
  "microservices_vs_monolith": "Detailed reasoning for the architecture choice, including trade-offs"
}}"""

    def parse_output(self, raw_response: str) -> dict:
        cleaned = self._clean_json_response(raw_response)
        data = json.loads(cleaned)
        required = ["architecture_type", "recommended_stack", "high_level_design",
                    "scalability_notes", "microservices_vs_monolith"]
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        return data
