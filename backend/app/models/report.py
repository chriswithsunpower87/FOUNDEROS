"""
File: app/models/report.py
Purpose: SQLAlchemy ORM models for agent reports.
Responsibilities:
  - Define AgentType enum for all 10 specialist agents
  - Define ReportStatus enum for per-agent lifecycle tracking
  - Map the reports table — one row per agent per idea
Dependencies:
  - app.models.base
  - sqlalchemy
"""

import enum
import uuid

from sqlalchemy import Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AgentType(str, enum.Enum):
    """
    Description: Identifies which specialist AI agent produced a report.
    """

    MARKET_RESEARCH      = "MARKET_RESEARCH"
    COMPETITOR_ANALYSIS  = "COMPETITOR_ANALYSIS"
    PRODUCT_MANAGER      = "PRODUCT_MANAGER"
    TECHNICAL_ARCHITECT  = "TECHNICAL_ARCHITECT"
    DATABASE_ARCHITECT   = "DATABASE_ARCHITECT"
    API_DESIGN           = "API_DESIGN"
    UIUX                 = "UIUX"
    ROADMAP              = "ROADMAP"
    MARKETING            = "MARKETING"
    RISK_ANALYSIS        = "RISK_ANALYSIS"


class ReportStatus(str, enum.Enum):
    """
    Description: Tracks the execution state of a single agent's report.
    """

    PENDING   = "PENDING"
    RUNNING   = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED    = "FAILED"


class Report(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Description: Stores the output of one AI agent for one startup idea.
    Responsibilities:
      - Hold structured JSON output from the agent
      - Track execution status and timing
      - Link to agent run traces for the trace view feature
    """

    __tablename__ = "reports"

    idea_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ideas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agent_type: Mapped[AgentType] = mapped_column(
        SAEnum(AgentType, name="agent_type"),
        nullable=False,
        index=True,
    )
    status: Mapped[ReportStatus] = mapped_column(
        SAEnum(ReportStatus, name="report_status"),
        default=ReportStatus.PENDING,
        nullable=False,
        index=True,
    )
    output: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    reasoning_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    execution_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Many reports → one idea
    idea: Mapped["Idea"] = relationship("Idea", back_populates="reports")  # noqa: F821

    # One report → many agent run traces
    agent_runs: Mapped[list["AgentRun"]] = relationship(  # noqa: F821
        "AgentRun",
        back_populates="report",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Report agent={self.agent_type} status={self.status}>"
