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

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.dependencies import get_current_user
from app.models.report import Report
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.report import AgentRunResponse, ReportResponse
from app.services.idea_service import IdeaService
from app.services.report_service import ReportService

router = APIRouter(prefix="/ideas", tags=["Reports"])


@router.get(
    "/{idea_id}/reports",
    response_model=APIResponse[list[ReportResponse]],
    summary="Get agent reports for an idea, optionally filtered by version",
)
async def get_reports(
    idea_id: uuid.UUID,
    version: int | None = Query(None, description="Analysis version (default: latest)"),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[list[ReportResponse]]:
    """
    Purpose: Return agent reports for an idea.
      - Without ?version: returns the latest analysis version.
      - With ?version=N: returns that specific historical version.
      Used by the frontend to display agent outputs and track progress.
    Parameters:
      idea_id: UUID of the idea.
      version: Optional version filter. Defaults to latest.
      db: Async database session.
      current_user: Authenticated user from JWT.
    Returns:
      APIResponse containing list of reports for the requested version.
    """
    idea_service = IdeaService(db)
    await idea_service.get_idea(idea_id=idea_id, user_id=current_user.id)

    report_service = ReportService(db)
    reports = await report_service.get_reports_for_idea(
        idea_id=idea_id,
        version=version,
    )

    return APIResponse(data=[ReportResponse.model_validate(r) for r in reports])


@router.get(
    "/{idea_id}/versions",
    response_model=APIResponse[list[int]],
    summary="Get all available analysis version numbers for an idea",
)
async def get_versions(
    idea_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[list[int]]:
    """
    Purpose: Return the list of analysis version numbers available for an idea.
      Used by the frontend version picker (e.g. [1, 2, 3] = analyzed 3 times).
    Parameters:
      idea_id: UUID of the idea.
      db: Async database session.
      current_user: Authenticated user from JWT.
    Returns:
      APIResponse containing sorted list of version integers (ascending).
    """
    idea_service = IdeaService(db)
    await idea_service.get_idea(idea_id=idea_id, user_id=current_user.id)

    from sqlalchemy import distinct, func
    result = await db.execute(
        select(distinct(Report.version))
        .where(Report.idea_id == idea_id)
        .order_by(Report.version)
    )
    versions = [row[0] for row in result.fetchall()]
    return APIResponse(data=versions)


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
