"""
File: app/models/agent_run.py
Purpose: SQLAlchemy ORM model for agent execution traces.
Responsibilities:
  - Record every individual agent execution attempt
  - Store prompt, input/output snapshots, model used, token count
  - Power the Agent Trace View feature in the frontend
Dependencies:
  - app.models.base
  - sqlalchemy
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin
from app.models.report import ReportStatus


class AgentRun(Base, UUIDPrimaryKeyMixin):
    """
    Description: Records a single agent execution attempt for traceability.
    Responsibilities:
      - Capture the full prompt sent to the LLM
      - Store the raw input/output state snapshots
      - Track timing and token usage for monitoring
      - Enable the Agent Trace View in the UI
    """

    __tablename__ = "agent_runs"

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    input_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    output_snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    prompt_used: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_used: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tokens_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[ReportStatus] = mapped_column(
        SAEnum(ReportStatus, name="report_status"),
        default=ReportStatus.RUNNING,
        nullable=False,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Many agent runs → one report
    report: Mapped["Report"] = relationship("Report", back_populates="agent_runs")  # noqa: F821

    def __repr__(self) -> str:
        return f"<AgentRun agent={self.agent_name} status={self.status}>"
