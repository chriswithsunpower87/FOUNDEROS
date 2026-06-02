"""
File: app/api/v1/reports.py
Purpose: FastAPI route handlers for fetching agent reports and trace data.
Responsibilities:
  - GET /ideas/{id}/reports — list all agent reports (polled by frontend)
  - GET /ideas/{id}/trace — list all agent run traces (for trace view)
Dependencies:
  - app.services.report_service (ReportService)
  - app.services.idea_service (IdeaService) — for ownership check
  - app.core.dependencies (get_current_user)
"""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.report import AgentRunResponse, ReportResponse
from app.services.idea_service import IdeaService
from app.services.report_service import ReportService

router = APIRouter(prefix="/ideas", tags=["Reports"])


@router.get(
    "/{idea_id}/reports",
    response_model=APIResponse[list[ReportResponse]],
    summary="Get all agent reports for an idea (poll every 3s during analysis)",
)
async def get_reports(
    idea_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[list[ReportResponse]]:
    """
    Purpose: Return all 10 agent report rows for an idea.
      Used by the frontend to poll progress during pipeline execution.
    Parameters:
      idea_id: UUID of the idea.
      db: Async database session.
      current_user: Authenticated user from JWT.
    Returns:
      APIResponse containing list of reports (some may still be PENDING/RUNNING).
    """
    # Verify ownership
    idea_service = IdeaService(db)
    await idea_service.get_idea(idea_id=idea_id, user_id=current_user.id)

    report_service = ReportService(db)
    reports = await report_service.get_reports_for_idea(idea_id=idea_id)

    return APIResponse(
        data=[ReportResponse.model_validate(r) for r in reports]
    )


@router.get(
    "/{idea_id}/trace",
    response_model=APIResponse[list[AgentRunResponse]],
    summary="Get agent execution traces for the trace view",
)
async def get_trace(
    idea_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[list[AgentRunResponse]]:
    """
    Purpose: Return all agent run trace records for an idea.
      Used by the Agent Trace View feature — shows prompt, model, tokens, etc.
    Parameters:
      idea_id: UUID of the idea.
      db: Async database session.
      current_user: Authenticated user from JWT.
    Returns:
      APIResponse containing list of agent run traces.
    """
    # Verify ownership
    idea_service = IdeaService(db)
    await idea_service.get_idea(idea_id=idea_id, user_id=current_user.id)

    report_service = ReportService(db)
    traces = await report_service.get_trace_for_idea(idea_id=idea_id)

    return APIResponse(
        data=[AgentRunResponse.model_validate(t) for t in traces]
    )
