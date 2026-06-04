"""Add version column to reports and analysis_count to ideas

Revision ID: 004
Revises: 003
Create Date: 2026-06-04

Purpose:
  - Adds `version` integer to reports (which analysis run this belongs to)
  - Adds `analysis_count` integer to ideas (how many times analyzed)
  - Existing rows default to version=1, analysis_count=1
  - Enables keeping full history of every re-analysis
"""

from alembic import op
import sqlalchemy as sa

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Purpose: Add versioning columns.
      - reports.version: which analysis run produced this report (1, 2, 3...)
      - ideas.analysis_count: how many times this idea has been analyzed
    """
    # Add version to reports (existing rows become version 1)
    op.add_column(
        "reports",
        sa.Column(
            "version",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
        ),
    )

    # Add index for fast version-filtered queries
    op.create_index(
        "ix_reports_idea_id_version",
        "reports",
        ["idea_id", "version"],
    )

    # Add analysis_count to ideas (existing rows become count 1)
    op.add_column(
        "ideas",
        sa.Column(
            "analysis_count",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
        ),
    )


def downgrade() -> None:
    op.drop_index("ix_reports_idea_id_version", table_name="reports")
    op.drop_column("reports", "version")
    op.drop_column("ideas", "analysis_count")
