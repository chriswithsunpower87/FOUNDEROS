"""
File: app/api/v1/ideas.py
Purpose: FastAPI route handlers for startup idea CRUD and pipeline trigger.
Responsibilities:
  - GET /ideas — list all ideas for authenticated user
  - POST /ideas — create a new idea
  - GET /ideas/{id} — get a single idea
  - PUT /ideas/{id} — update an idea
  - DELETE /ideas/{id} — delete an idea
  - POST /ideas/{id}/analyze — trigger the AI agent pipeline
Dependencies:
  - app.services.idea_service (IdeaService)
  - app.agents.orchestrator (run_pipeline_background)
  - app.core.dependencies (get_current_user)
"""

import asyncio
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.orchestrator import run_pipeline_background
from app.core.database import get_async_db
from app.core.dependencies import get_current_user
from app.core.limiter import limiter
from app.models.idea import IdeaStatus
from app.models.user import User
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.idea import CreateIdeaRequest, IdeaResponse, UpdateIdeaRequest
from app.services.idea_service import IdeaService

router = APIRouter(prefix="/ideas", tags=["Ideas"])


@router.post(
    "",
    response_model=APIResponse[IdeaResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new startup idea",
)
async def create_idea(
    payload: CreateIdeaRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[IdeaResponse]:
    """
    Purpose: Create a new startup idea for the authenticated user.
    Parameters:
      payload: Idea data (title, problem_statement, target_audience).
      db: Async database session.
      current_user: Authenticated user from JWT.
    Returns:
      APIResponse containing the created idea.
    """
    service = IdeaService(db)
    idea = await service.create_idea(user_id=current_user.id, payload=payload)
    return APIResponse(
        data=IdeaResponse.model_validate(idea),
        message="Idea created successfully",
    )


@router.get(
    "",
    response_model=APIResponse[PaginatedResponse[IdeaResponse]],
    summary="List all ideas for the current user",
)
async def list_ideas(
    status_filter: IdeaStatus | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[PaginatedResponse[IdeaResponse]]:
    """
    Purpose: Return a paginated list of the current user's ideas.
    Parameters:
      status_filter: Optional filter by IdeaStatus.
      page: Page number (default 1).
      page_size: Items per page (default 20, max 100).
      db: Async database session.
      current_user: Authenticated user from JWT.
    Returns:
      APIResponse containing paginated ideas.
    """
    service = IdeaService(db)
    ideas, total = await service.list_ideas(
        user_id=current_user.id,
        status_filter=status_filter,
        page=page,
        page_size=page_size,
    )

    return APIResponse(
        data=PaginatedResponse(
            items=[IdeaResponse.model_validate(i) for i in ideas],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.get(
    "/{idea_id}",
    response_model=APIResponse[IdeaResponse],
    summary="Get a single idea by ID",
)
async def get_idea(
    idea_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[IdeaResponse]:
    """
    Purpose: Fetch a single idea, verifying the user owns it.
    Parameters:
      idea_id: UUID of the idea.
      db: Async database session.
      current_user: Authenticated user from JWT.
    Returns:
      APIResponse containing the idea.
    """
    service = IdeaService(db)
    idea = await service.get_idea(idea_id=idea_id, user_id=current_user.id)
    return APIResponse(data=IdeaResponse.model_validate(idea))


@router.put(
    "/{idea_id}",
    response_model=APIResponse[IdeaResponse],
    summary="Update an idea (only when status is DRAFT)",
)
async def update_idea(
    idea_id: uuid.UUID,
    payload: UpdateIdeaRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[IdeaResponse]:
    """
    Purpose: Update idea metadata. Only permitted when status is DRAFT.
    """
    service = IdeaService(db)
    idea = await service.update_idea(idea_id=idea_id, user_id=current_user.id, payload=payload)
    return APIResponse(data=IdeaResponse.model_validate(idea), message="Idea updated")


@router.delete(
    "/{idea_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an idea and all its reports",
)
async def delete_idea(
    idea_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Purpose: Delete an idea and cascade-delete all associated reports.
    """
    service = IdeaService(db)
    await service.delete_idea(idea_id=idea_id, user_id=current_user.id)


@router.post(
    "/{idea_id}/analyze",
    response_model=APIResponse[dict],
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger the 11-agent AI analysis pipeline",
)
@limiter.limit("5/day")          # 5 analyses per user per day
async def analyze_idea(
    request: Request,              # Required by SlowAPI for rate limit key extraction
    idea_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[dict]:
    """
    Purpose: Queue the AI pipeline to run asynchronously.
      Creates 10 PENDING report stubs, sets idea to PENDING,
      and launches the LangGraph orchestrator in a background task.
    Parameters:
      idea_id: UUID of the idea to analyze.
      background_tasks: FastAPI background task runner.
      db: Async database session.
      current_user: Authenticated user from JWT.
    Returns:
      202 Accepted — pipeline has been queued.
    """
    service = IdeaService(db)
    idea = await service.trigger_analysis(idea_id=idea_id, user_id=current_user.id)

    # Launch the LangGraph pipeline in a background thread (non-blocking)
    background_tasks.add_task(
        run_pipeline_background,
        idea_id=str(idea.id),
        idea_title=idea.title,
        problem_statement=idea.problem_statement,
        target_audience=idea.target_audience,
    )

    return APIResponse(
        data={"idea_id": str(idea.id), "status": idea.status.value},
        message="Analysis pipeline started. Poll /ideas/{id}/reports for progress.",
    )
