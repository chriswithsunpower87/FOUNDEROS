"""
File: app/services/idea_service.py
Purpose: Business logic for startup idea CRUD operations.
Responsibilities:
  - Create, read, update, delete ideas (scoped to the authenticated user)
  - Enforce ownership — users can only access their own ideas
  - Trigger the analysis pipeline (update status, create report stubs)
Dependencies:
  - sqlalchemy.ext.asyncio (AsyncSession)
  - app.models.idea (Idea, IdeaStatus)
  - app.models.report (Report, AgentType, ReportStatus)
  - app.schemas.idea (CreateIdeaRequest, UpdateIdeaRequest)
"""

import uuid
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.idea import Idea, IdeaStatus
from app.models.report import AgentType, Report, ReportStatus
from app.schemas.idea import CreateIdeaRequest, UpdateIdeaRequest

# All 11 agents in pipeline execution order
ALL_AGENT_TYPES = [
    AgentType.MARKET_RESEARCH,
    AgentType.COMPETITOR_ANALYSIS,
    AgentType.PRODUCT_MANAGER,
    AgentType.TECHNICAL_ARCHITECT,
    AgentType.DATABASE_ARCHITECT,
    AgentType.API_DESIGN,
    AgentType.UIUX,
    AgentType.ROADMAP,
    AgentType.MARKETING,
    AgentType.RISK_ANALYSIS,
    AgentType.REVENUE_COST,    # Agent 11 — Revenue Model & Cost Estimation
]


class IdeaService:
    """
    Description: Manages all business logic for idea operations.
    Responsibilities:
      - CRUD operations with user ownership enforcement
      - Pipeline trigger logic (create report stubs, update status)
    """

    def __init__(self, db: AsyncSession):
        """
        Purpose: Initialize with injected async database session.
        Parameters:
          db: Async SQLAlchemy session.
        """
        self.db = db

    async def create_idea(self, user_id: uuid.UUID, payload: CreateIdeaRequest) -> Idea:
        """
        Purpose: Create a new startup idea for the given user.
        Parameters:
          user_id: UUID of the authenticated user.
          payload: Validated idea data.
        Returns:
          Idea: Newly created Idea ORM object.
        """
        idea = Idea(
            user_id=user_id,
            title=payload.title,
            problem_statement=payload.problem_statement,
            target_audience=payload.target_audience,
            status=IdeaStatus.DRAFT,
        )
        self.db.add(idea)
        await self.db.flush()
        await self.db.refresh(idea)
        return idea

    async def list_ideas(
        self,
        user_id: uuid.UUID,
        status_filter: Optional[IdeaStatus] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Idea], int]:
        """
        Purpose: List all ideas belonging to the authenticated user.
        Parameters:
          user_id: UUID of the authenticated user.
          status_filter: Optional filter by idea status.
          page: Page number (1-indexed).
          page_size: Number of items per page.
        Returns:
          tuple[list[Idea], int]: List of ideas and total count.
        """
        query = select(Idea).where(Idea.user_id == user_id)
        count_query = select(func.count()).select_from(Idea).where(Idea.user_id == user_id)

        if status_filter:
            query = query.where(Idea.status == status_filter)
            count_query = count_query.where(Idea.status == status_filter)

        query = query.order_by(Idea.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        count_result = await self.db.execute(count_query)

        return result.scalars().all(), count_result.scalar()

    async def get_idea(self, idea_id: uuid.UUID, user_id: uuid.UUID) -> Idea:
        """
        Purpose: Get a single idea, verifying ownership.
        Parameters:
          idea_id: UUID of the idea to fetch.
          user_id: UUID of the authenticated user.
        Returns:
          Idea: The requested idea.
        Raises:
          HTTPException 404: If idea not found or belongs to another user.
        """
        result = await self.db.execute(
            select(Idea).where(Idea.id == idea_id, Idea.user_id == user_id)
        )
        idea = result.scalar_one_or_none()
        if not idea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Idea {idea_id} not found",
            )
        return idea

    async def update_idea(
        self, idea_id: uuid.UUID, user_id: uuid.UUID, payload: UpdateIdeaRequest
    ) -> Idea:
        """
        Purpose: Update idea metadata. Only allowed when status is DRAFT.
        Parameters:
          idea_id: UUID of the idea to update.
          user_id: UUID of the authenticated user.
          payload: Fields to update (all optional).
        Returns:
          Idea: The updated idea.
        Raises:
          HTTPException 400: If idea status is not DRAFT.
        """
        idea = await self.get_idea(idea_id, user_id)

        if idea.status != IdeaStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only DRAFT ideas can be edited. The analysis has already begun.",
            )

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(idea, field, value)

        await self.db.flush()
        await self.db.refresh(idea)
        return idea

    async def delete_idea(self, idea_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """
        Purpose: Delete an idea and all associated reports (cascade).
        Parameters:
          idea_id: UUID of the idea to delete.
          user_id: UUID of the authenticated user.
        """
        idea = await self.get_idea(idea_id, user_id)
        await self.db.delete(idea)
        await self.db.flush()

    async def trigger_analysis(self, idea_id: uuid.UUID, user_id: uuid.UUID) -> Idea:
        """
        Purpose: Prepare the idea for pipeline execution.
          Resets or creates one PENDING report stub per agent (handles re-runs).
          Sets idea status to PENDING.
        Parameters:
          idea_id: UUID of the idea to analyze.
          user_id: UUID of the authenticated user.
        Returns:
          Idea: Updated idea with PENDING status.
        Raises:
          HTTPException 400: If idea is already being processed or completed.
        """
        idea = await self.get_idea(idea_id, user_id)

        if idea.status in (IdeaStatus.PROCESSING, IdeaStatus.PENDING):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Analysis is already running for this idea",
            )

        # Fetch any existing reports for this idea
        existing_result = await self.db.execute(
            select(Report).where(Report.idea_id == idea.id)
        )
        existing_reports = {r.agent_type: r for r in existing_result.scalars().all()}

        for agent_type in ALL_AGENT_TYPES:
            if agent_type in existing_reports:
                # Reset existing report to PENDING so it re-runs cleanly
                report = existing_reports[agent_type]
                report.status = ReportStatus.PENDING
                report.output = None
                report.reasoning_summary = None
                report.error_message = None
                report.execution_time_ms = None
            else:
                # First time — create a fresh stub
                self.db.add(Report(
                    idea_id=idea.id,
                    agent_type=agent_type,
                    status=ReportStatus.PENDING,
                ))

        idea.status = IdeaStatus.PENDING
        await self.db.flush()
        await self.db.refresh(idea)
        return idea
