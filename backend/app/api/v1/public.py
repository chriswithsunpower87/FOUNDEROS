"""
File: app/api/v1/public.py
Purpose: Public (unauthenticated) endpoints for shareable blueprint links.
Responsibilities:
  - GET /public/blueprints/{id} — return a public idea + its reports (no auth)
  - POST /ideas/{id}/toggle-public — toggle is_public on/off (requires auth)
Dependencies:
  - app.models.idea (Idea)
  - app.models.report (Report)
  - app.schemas.idea (IdeaResponse)
  - app.schemas.report (ReportResponse)
  - app.core.dependencies (get_current_user)
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.dependencies import get_current_user
from app.models.idea import Idea
from app.models.report import Report
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.idea import IdeaResponse
from app.schemas.report import ReportResponse

router = APIRouter(tags=["Public"])


@router.get(
    "/public/blueprints/{idea_id}",
    response_model=APIResponse[dict],
    summary="View a public startup blueprint (no login required)",
)
async def get_public_blueprint(
    idea_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
) -> APIResponse[dict]:
    """
    Purpose: Return a completed startup blueprint for a public idea.
      No authentication required — anyone with the link can view it.
      Only returns the blueprint if is_public=True AND status=COMPLETED.
    Parameters:
      idea_id: UUID of the idea to view.
      db: Async database session.
    Returns:
      APIResponse containing the idea metadata and all 11 agent reports.
    Raises:
      404: If idea doesn't exist, is not public, or is not completed.
    """
    # Fetch the idea — must be public and completed
    result = await db.execute(
        select(Idea).where(
            Idea.id == idea_id,
            Idea.is_public == True,  # noqa: E712
        )
    )
    idea = result.scalar_one_or_none()

    if not idea or idea.status.value != "COMPLETED":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blueprint not found or not publicly shared",
        )

    # Fetch all completed reports
    reports_result = await db.execute(
        select(Report).where(Report.idea_id == idea_id)
    )
    reports = reports_result.scalars().all()

    return APIResponse(
        data={
            "idea": IdeaResponse.model_validate(idea).model_dump(),
            "reports": [ReportResponse.model_validate(r).model_dump() for r in reports],
        },
        message="Public blueprint retrieved successfully",
    )


@router.post(
    "/ideas/{idea_id}/toggle-public",
    response_model=APIResponse[IdeaResponse],
    summary="Toggle whether this blueprint is publicly shareable",
)
async def toggle_public(
    idea_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[IdeaResponse]:
    """
    Purpose: Flip is_public on the idea owned by the current user.
      When is_public=True, anyone with the blueprint URL can view it without logging in.
      Only completed blueprints can be made public.
    Parameters:
      idea_id: UUID of the idea to toggle.
      db: Async database session.
      current_user: Authenticated user from JWT.
    Returns:
      Updated idea with new is_public value.
    Raises:
      404: If idea not found or not owned by user.
      400: If idea is not completed (can't share incomplete blueprints).
    """
    result = await db.execute(
        select(Idea).where(Idea.id == idea_id, Idea.user_id == current_user.id)
    )
    idea = result.scalar_one_or_none()

    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Idea {idea_id} not found",
        )

    if idea.status.value != "COMPLETED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only completed blueprints can be made public",
        )

    # Toggle is_public
    idea.is_public = not idea.is_public
    await db.flush()
    await db.refresh(idea)

    action = "published" if idea.is_public else "unpublished"
    return APIResponse(
        data=IdeaResponse.model_validate(idea),
        message=f"Blueprint {action} successfully",
    )
