"""Add REVENUE_COST to agent_type enum

Revision ID: 002
Revises: 001
Create Date: 2026-06-03

Purpose:
  - Adds the REVENUE_COST value to the agent_type PostgreSQL enum
  - Required for Agent 11 (Revenue & Cost Agent)
  - Uses IF NOT EXISTS so re-running is safe
"""

from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Purpose: Add REVENUE_COST to the agent_type enum.
    Notes:
      - PostgreSQL requires ALTER TYPE to add enum values.
      - IF NOT EXISTS prevents failure if the migration is run twice.
      - Enum values cannot be removed in PostgreSQL without dropping the column,
        so downgrade is intentionally a no-op.
    """
    # Commit the current transaction before altering the enum
    # (PostgreSQL requires ALTER TYPE outside a transaction block)
    op.execute("COMMIT")
    op.execute("ALTER TYPE agent_type ADD VALUE IF NOT EXISTS 'REVENUE_COST'")


def downgrade() -> None:
    """
    Purpose: No-op — PostgreSQL does not support removing enum values.
    If a rollback is needed, drop and recreate the type manually.
    """
    pass
