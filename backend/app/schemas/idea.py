"""
File: app/schemas/idea.py
Purpose: Pydantic request/response schemas for idea endpoints.
Responsibilities:
  - Validate create and update request bodies for ideas
  - Define the shape of idea responses
Dependencies:
  - pydantic
  - app.models.idea (IdeaStatus)
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.idea import IdeaStatus


class CreateIdeaRequest(BaseModel):
    """
    Description: Request body for POST /ideas.
    """

    title: str = Field(
        ...,
        min_length=3,
        max_length=200,
        examples=["AI Fitness App"],
    )
    problem_statement: str = Field(
        ...,
        min_length=10,
        examples=["People struggle to stay consistent with workouts without coaching"],
    )
    target_audience: str = Field(
        ...,
        min_length=5,
        max_length=500,
        examples=["Busy professionals aged 25-40 who want personalized fitness plans"],
    )


class UpdateIdeaRequest(BaseModel):
    """
    Description: Request body for PUT /ideas/{id} — all fields optional.
    """

    title: str | None = Field(None, min_length=3, max_length=200)
    problem_statement: str | None = Field(None, min_length=10)
    target_audience: str | None = Field(None, min_length=5, max_length=500)


class IdeaResponse(BaseModel):
    """
    Description: Full idea data returned in API responses.
    """

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    problem_statement: str
    target_audience: str
    status: IdeaStatus
    is_public: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
