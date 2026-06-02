"""
File: app/models/user.py
Purpose: SQLAlchemy ORM model for the users table.
Responsibilities:
  - Map the users PostgreSQL table to a Python class
  - Define the relationship to the ideas table
Dependencies:
  - app.models.base (Base, TimestampMixin, UUIDPrimaryKeyMixin)
  - sqlalchemy
"""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Description: Represents a registered FounderOS user.
    Responsibilities:
      - Store user credentials (email + bcrypt hash)
      - Link to all ideas owned by the user
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # One user → many ideas
    ideas: Mapped[list["Idea"]] = relationship(  # noqa: F821
        "Idea",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
