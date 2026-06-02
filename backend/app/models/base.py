"""
File: app/models/base.py
Purpose: SQLAlchemy declarative base and shared mixins for all ORM models.
Responsibilities:
  - Define the DeclarativeBase all models inherit from
  - Provide a TimestampMixin with created_at and updated_at columns
  - Provide a UUIDPrimaryKeyMixin for consistent UUID primary keys
Dependencies:
  - sqlalchemy
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Description: SQLAlchemy declarative base class.
    Responsibilities:
      - Serves as the parent class for all ORM models
      - Enables Alembic autogenerate to detect all models
    """
    pass


class TimestampMixin:
    """
    Description: Mixin that adds created_at and updated_at to any model.
    Responsibilities:
      - Auto-set created_at on INSERT via server_default
      - Auto-update updated_at on UPDATE via onupdate
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class UUIDPrimaryKeyMixin:
    """
    Description: Mixin that adds a UUID primary key column.
    Responsibilities:
      - Generate a UUID v4 for every new row automatically
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
