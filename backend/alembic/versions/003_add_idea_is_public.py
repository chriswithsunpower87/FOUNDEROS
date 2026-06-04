"""Add is_public field to ideas table

Revision ID: 003
Revises: 002
Create Date: 2026-06-04

Purpose:
  - Adds is_public boolean to the ideas table (default FALSE)
  - Enables shareable public blueprint URLs (no auth required to view)
  - Public ideas are accessible via GET /api/v1/public/blueprints/{id}
"""

from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Purpose: Add is_public column to the ideas table.
      Defaults to FALSE so existing ideas remain private.
    """
    op.add_column(
        "ideas",
        sa.Column(
            "is_public",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("FALSE"),
        ),
    )


def downgrade() -> None:
    """
    Purpose: Remove the is_public column.
    """
    op.drop_column("ideas", "is_public")
