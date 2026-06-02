"""
File: app/models/idea.py
Purpose: SQLAlchemy ORM model for the ideas table.
Responsibilities:
  - Map the ideas PostgreSQL table to a Python class
  - Define IdeaStatus enum for pipeline state tracking
  - Define relationships to User and Report models
Dependencies:
  - app.models.base (Base, TimestampMixin, UUIDPrimaryKeyMixin)
  - sqlalchemy
"""

import enum
import uuid

from sqlalchemy import Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class IdeaStatus(str, enum.Enum):
    """
    Description: Tracks the lifecycle state of an idea's analysis pipeline.
    Values:
      DRAFT      — Idea created, analysis not yet triggered
      PENDING    — Analysis queued, about to start
      PROCESSING — Agent pipeline is currently running
      COMPLETED  — All agents finished successfully
      FAILED     — Pipeline encountered a fatal error
    """

    DRAFT      = "DRAFT"
    PENDING    = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED  = "COMPLETED"
    FAILED     = "FAILED"


class Idea(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Description: Represents a startup idea created by a user.
    Responsibilities:
      - Store the core idea inputs (title, problem, audience)
      - Track the analysis pipeline status
      - Link to all generated agent reports
    """

    __tablename__ = "ideas"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    problem_statement: Mapped[str] = mapped_column(Text, nullable=False)
    target_audience: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[IdeaStatus] = mapped_column(
        SAEnum(IdeaStatus, name="idea_status"),
        default=IdeaStatus.DRAFT,
        nullable=False,
        index=True,
    )

    # Many ideas → one user
    user: Mapped["User"] = relationship("User", back_populates="ideas")  # noqa: F821

    # One idea → many reports (one per agent)
    reports: Mapped[list["Report"]] = relationship(  # noqa: F821
        "Report",
        back_populates="idea",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Idea id={self.id} title={self.title!r} status={self.status}>"
