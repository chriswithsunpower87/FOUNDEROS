"""
File: app/schemas/report.py
Purpose: Pydantic schemas for report and agent run responses + all agent output shapes.
Responsibilities:
  - Define the response shape for report and agent run endpoints
  - Define typed Pydantic models for each agent's JSON output
  - These output schemas are used both for response docs and LLM output validation
Dependencies:
  - pydantic
  - app.models.report (AgentType, ReportStatus)
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.report import AgentType, ReportStatus


# ─────────────────────────────────────────────────────────────────────────────
# Agent Output Schemas
# Each schema matches the JSONB structure stored in reports.output
# ─────────────────────────────────────────────────────────────────────────────

class MarketResearchOutput(BaseModel):
    industry_overview: str
    market_size: str
    market_trends: list[str]
    market_opportunities: list[str]
    potential_demand: str
    target_segments: list[str]


class Competitor(BaseModel):
    name: str
    description: str
    strengths: list[str]
    weaknesses: list[str]


class CompetitorAnalysisOutput(BaseModel):
    competitors: list[Competitor]
    market_gaps: list[str]
    differentiation_opportunities: list[str]


class UserStory(BaseModel):
    role: str
    action: str
    benefit: str
    acceptance_criteria: list[str]


class ProductManagerOutput(BaseModel):
    product_vision: str
    core_features: list[str]
    user_stories: list[UserStory]
    prd_summary: str


class TechStack(BaseModel):
    frontend: str
    backend: str
    database: str
    infrastructure: str


class TechnicalArchitectOutput(BaseModel):
    architecture_type: str
    recommended_stack: TechStack
    high_level_design: str
    scalability_notes: list[str]
    microservices_vs_monolith: str


class Entity(BaseModel):
    name: str
    columns: list[str]
    description: str


class DatabaseArchitectOutput(BaseModel):
    entities: list[Entity]
    relationships: list[str]
    sql_schema: str
    design_notes: str


class APIEndpoint(BaseModel):
    method: str
    path: str
    description: str
    request_example: dict[str, Any]
    response_example: dict[str, Any]


class APIDesignOutput(BaseModel):
    endpoints: list[APIEndpoint]
    design_notes: str


class Screen(BaseModel):
    name: str
    description: str
    components: list[str]
    user_flow: str


class UIUXOutput(BaseModel):
    screens: list[Screen]
    design_principles: list[str]
    color_scheme: str
    typography: str


class WeekPlan(BaseModel):
    week: int
    focus: str
    deliverables: list[str]
    milestone: str


class RoadmapOutput(BaseModel):
    mvp_duration_weeks: int
    weeks: list[WeekPlan]
    definition_of_done: str


class MarketingChannel(BaseModel):
    channel: str
    rationale: str
    estimated_cost: str


class MarketingOutput(BaseModel):
    ideal_customer_profile: str
    marketing_channels: list[MarketingChannel]
    launch_strategy: str
    growth_tactics: list[str]


class Risk(BaseModel):
    title: str
    description: str
    severity: str = Field(..., pattern="^(HIGH|MEDIUM|LOW)$")
    mitigation: str


class RiskAnalysisOutput(BaseModel):
    risks: list[Risk]
    key_assumptions: list[str]
    failure_points: list[str]
    overall_risk_level: str


# ─────────────────────────────────────────────────────────────────────────────
# API Response Schemas
# ─────────────────────────────────────────────────────────────────────────────

class ReportResponse(BaseModel):
    """
    Description: Single agent report returned by the reports endpoint.
    """

    id: uuid.UUID
    idea_id: uuid.UUID
    agent_type: AgentType
    status: ReportStatus
    output: dict[str, Any] | None
    reasoning_summary: str | None
    error_message: str | None
    execution_time_ms: int | None
    version: int           # Which analysis run this report belongs to (1, 2, 3...)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AgentRunResponse(BaseModel):
    """
    Description: Single agent execution trace returned by the trace endpoint.
    """

    id: uuid.UUID
    report_id: uuid.UUID
    agent_name: str
    input_snapshot: dict[str, Any]
    output_snapshot: dict[str, Any] | None
    prompt_used: str | None
    model_used: str | None
    tokens_used: int | None
    status: ReportStatus
    error_message: str | None
    started_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}
