"""
File: app/agents/database_architect_agent.py
Purpose: Agent 5 — designs the database schema for the startup.
Responsibilities:
  - Define entities, relationships, and SQL schema
  - Read from Technical Architect and Product Manager outputs
Dependencies:
  - app.agents.base_agent (BaseAgent)
"""

import json
from app.agents.base_agent import BaseAgent
from app.agents.state import PipelineState
from app.models.report import AgentType


class DatabaseArchitectAgent(BaseAgent):
    """
    Description: Database Architect agent that designs the data model.
    Responsibilities:
      - Identify core entities from the product requirements
      - Design normalized relational schema with indexes
    """

    agent_type = AgentType.DATABASE_ARCHITECT
    agent_name = "Database Architect Agent"

    def build_prompt(self, state: PipelineState) -> str:
        features_context = ""
        if state.get("product_manager"):
            features = state["product_manager"].get("core_features", [])
            features_context = f"Features requiring data: {', '.join(features[:5])}"

        stack_context = ""
        if state.get("technical_architect"):
            db = state["technical_architect"].get("recommended_stack", {}).get("database", "")
            stack_context = f"Recommended database: {db}"

        return f"""You are a Senior Database Architect with deep expertise in PostgreSQL and data modeling.
You design schemas that are normalized, performant, and easy to evolve.

STARTUP IDEA:
Title: {state['idea_title']}
Problem: {state['problem_statement']}
Target Audience: {state['target_audience']}

PRODUCT CONTEXT:
{features_context}

TECH STACK:
{stack_context}

TASK:
Design the database schema for this startup's MVP.

Respond ONLY with valid JSON:
{{
  "entities": [
    {{
      "name": "table_name",
      "columns": ["id UUID PK", "user_id UUID FK", "column_name TYPE constraint"],
      "description": "What this table stores"
    }}
  ],
  "relationships": [
    "users has many posts (user_id FK)",
    "posts has many comments (post_id FK)"
  ],
  "sql_schema": "Complete CREATE TABLE statements for all entities",
  "design_notes": "Key design decisions, indexing strategy, and normalization choices"
}}

Include 4-7 entities covering the core product features. Write real SQL in sql_schema."""

    def parse_output(self, raw_response: str) -> dict:
        cleaned = self._clean_json_response(raw_response)
        data = json.loads(cleaned)
        required = ["entities", "relationships", "sql_schema", "design_notes"]
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        return data
