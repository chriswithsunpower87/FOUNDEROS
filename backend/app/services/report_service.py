"""
File: app/services/report_service.py
Purpose: Business logic for reading agent reports and trace data.
Responsibilities:
  - Fetch all reports for an idea (used for polling)
  - Fetch all agent run traces for the trace view feature
  - Update report status and output (called by agents via sync session)
Dependencies:
  - sqlalchemy (sync + async)
  - app.models.report (Report, AgentType, ReportStatus)
  - app.models.agent_run (AgentRun)
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.models.agent_run import AgentRun
from app.models.report import AgentType, Report, ReportStatus


class ReportService:
    """
    Description: Reads report and trace data for API responses.
    Responsibilities:
      - Provide reports list for the workspace polling endpoint
      - Provide agent run traces for the trace view
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_reports_for_idea(self, idea_id: uuid.UUID) -> list[Report]:
        """
        Purpose: Fetch all agent reports for a given idea.
        Parameters:
          idea_id: UUID of the idea.
        Returns:
          list[Report]: All 10 report rows (including pending/running ones).
        """
        result = await self.db.execute(
            select(Report)
            .where(Report.idea_id == idea_id)
            .order_by(Report.agent_type)
        )
        return result.scalars().all()

    async def get_trace_for_idea(self, idea_id: uuid.UUID) -> list[AgentRun]:
        """
        Purpose: Fetch all agent run traces for a given idea's reports.
        Parameters:
          idea_id: UUID of the idea.
        Returns:
          list[AgentRun]: All agent run records ordered by start time.
        """
        result = await self.db.execute(
            select(AgentRun)
            .join(Report, AgentRun.report_id == Report.id)
            .where(Report.idea_id == idea_id)
            .order_by(AgentRun.started_at)
        )
        return result.scalars().all()


# ── Sync helpers called by agents running in background threads ───────────────

def sync_update_report_running(
    db: Session, idea_id: uuid.UUID, agent_type: AgentType
) -> Report:
    """
    Purpose: Mark a report as RUNNING when an agent begins execution.
    Parameters:
      db: Synchronous SQLAlchemy session.
      idea_id: UUID of the parent idea.
      agent_type: Which agent is starting.
    Returns:
      Report: Updated report ORM object.
    """
    report = db.execute(
        select(Report).where(
            Report.idea_id == idea_id,
            Report.agent_type == agent_type,
        )
    ).scalar_one()

    report.status = ReportStatus.RUNNING
    db.commit()
    db.refresh(report)
    return report


def sync_save_report_output(
    db: Session,
    idea_id: uuid.UUID,
    agent_type: AgentType,
    output: dict[str, Any],
    reasoning_summary: str,
    execution_time_ms: int,
) -> Report:
    """
    Purpose: Save a completed agent's output to the database.
    Parameters:
      db: Synchronous SQLAlchemy session.
      idea_id: UUID of the parent idea.
      agent_type: Which agent produced this output.
      output: Structured JSON output from the agent.
      reasoning_summary: Human-readable agent summary.
      execution_time_ms: Execution duration in milliseconds.
    Returns:
      Report: Updated report with COMPLETED status.
    """
    report = db.execute(
        select(Report).where(
            Report.idea_id == idea_id,
            Report.agent_type == agent_type,
        )
    ).scalar_one()

    report.status = ReportStatus.COMPLETED
    report.output = output
    report.reasoning_summary = reasoning_summary
    report.execution_time_ms = execution_time_ms
    db.commit()
    db.refresh(report)
    return report


def sync_fail_report(
    db: Session,
    idea_id: uuid.UUID,
    agent_type: AgentType,
    error_message: str,
) -> None:
    """
    Purpose: Mark a report as FAILED and store the error message.
    Parameters:
      db: Synchronous SQLAlchemy session.
      idea_id: UUID of the parent idea.
      agent_type: Which agent failed.
      error_message: The exception or error description.
    """
    report = db.execute(
        select(Report).where(
            Report.idea_id == idea_id,
            Report.agent_type == agent_type,
        )
    ).scalar_one_or_none()

    if report:
        report.status = ReportStatus.FAILED
        report.error_message = error_message
        db.commit()


def sync_save_agent_run(
    db: Session,
    report_id: uuid.UUID,
    agent_name: str,
    input_snapshot: dict,
    output_snapshot: dict | None,
    prompt_used: str,
    model_used: str,
    tokens_used: int | None,
    status: ReportStatus,
    error_message: str | None,
    started_at: datetime,
) -> None:
    """
    Purpose: Persist a full agent execution trace for the trace view.
    Parameters:
      db: Synchronous SQLAlchemy session.
      report_id: UUID of the associated report.
      agent_name: Human-readable agent name.
      input_snapshot: The pipeline state passed into the agent.
      output_snapshot: The agent's output dict (or None if failed).
      prompt_used: The full prompt string sent to the LLM.
      model_used: Name of the LLM model used.
      tokens_used: Number of tokens consumed (if available).
      status: COMPLETED or FAILED.
      error_message: Error description if FAILED.
      started_at: When the agent started.
    """
    run = AgentRun(
        report_id=report_id,
        agent_name=agent_name,
        input_snapshot=input_snapshot,
        output_snapshot=output_snapshot,
        prompt_used=prompt_used,
        model_used=model_used,
        tokens_used=tokens_used,
        status=status,
        error_message=error_message,
        started_at=started_at,
        completed_at=datetime.now(timezone.utc),
    )
    db.add(run)
    db.commit()
