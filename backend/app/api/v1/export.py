"""
File: app/api/v1/export.py
Purpose: FastAPI route handlers for blueprint export (PDF and Markdown).
Responsibilities:
  - GET /ideas/{id}/export/pdf — download full blueprint as PDF
  - GET /ideas/{id}/export/markdown — download full blueprint as Markdown
Dependencies:
  - app.services.export_service (ExportService)
  - app.services.idea_service (IdeaService)
  - app.services.report_service (ReportService)
"""

import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.export_service import ExportService
from app.services.idea_service import IdeaService
from app.services.report_service import ReportService

router = APIRouter(prefix="/ideas", tags=["Export"])


@router.get(
    "/{idea_id}/export/pdf",
    summary="Export full startup blueprint as PDF",
)
async def export_pdf(
    idea_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    """
    Purpose: Generate and stream a PDF of the complete startup blueprint.
    Parameters:
      idea_id: UUID of the idea.
      db: Async database session.
      current_user: Authenticated user from JWT.
    Returns:
      Binary PDF response with appropriate Content-Disposition header.
    """
    idea_service = IdeaService(db)
    report_service = ReportService(db)

    idea = await idea_service.get_idea(idea_id=idea_id, user_id=current_user.id)
    reports = await report_service.get_reports_for_idea(idea_id=idea_id)

    exporter = ExportService(idea=idea, reports=reports)
    pdf_bytes = exporter.generate_pdf()

    safe_title = idea.title.lower().replace(" ", "-").replace("/", "-")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_title}-blueprint.pdf"'
        },
    )


@router.get(
    "/{idea_id}/export/markdown",
    summary="Export full startup blueprint as Markdown",
)
async def export_markdown(
    idea_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    """
    Purpose: Generate and stream a Markdown file of the complete startup blueprint.
    Parameters:
      idea_id: UUID of the idea.
      db: Async database session.
      current_user: Authenticated user from JWT.
    Returns:
      Markdown text response with appropriate Content-Disposition header.
    """
    idea_service = IdeaService(db)
    report_service = ReportService(db)

    idea = await idea_service.get_idea(idea_id=idea_id, user_id=current_user.id)
    reports = await report_service.get_reports_for_idea(idea_id=idea_id)

    exporter = ExportService(idea=idea, reports=reports)
    markdown_text = exporter.generate_markdown()

    safe_title = idea.title.lower().replace(" ", "-").replace("/", "-")

    return Response(
        content=markdown_text.encode("utf-8"),
        media_type="text/markdown",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_title}-blueprint.md"'
        },
    )
