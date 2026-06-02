"""Initial schema — users, ideas, reports, agent_runs

Revision ID: 001
Revises:
Create Date: 2026-06-02
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables for the initial FounderOS schema."""

    # ── Enum types ─────────────────────────────────────────────────────────────
    idea_status = postgresql.ENUM(
        "DRAFT", "PENDING", "PROCESSING", "COMPLETED", "FAILED",
        name="idea_status",
    )
    agent_type = postgresql.ENUM(
        "MARKET_RESEARCH", "COMPETITOR_ANALYSIS", "PRODUCT_MANAGER",
        "TECHNICAL_ARCHITECT", "DATABASE_ARCHITECT", "API_DESIGN",
        "UIUX", "ROADMAP", "MARKETING", "RISK_ANALYSIS",
        name="agent_type",
    )
    report_status = postgresql.ENUM(
        "PENDING", "RUNNING", "COMPLETED", "FAILED",
        name="report_status",
    )

    idea_status.create(op.get_bind(), checkfirst=True)
    agent_type.create(op.get_bind(), checkfirst=True)
    report_status.create(op.get_bind(), checkfirst=True)

    # ── users ──────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_users_email", "users", ["email"])

    # ── ideas ──────────────────────────────────────────────────────────────────
    op.create_table(
        "ideas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("problem_statement", sa.Text(), nullable=False),
        sa.Column("target_audience", sa.String(500), nullable=False),
        sa.Column("status", sa.Enum("DRAFT", "PENDING", "PROCESSING", "COMPLETED", "FAILED", name="idea_status"), nullable=False, server_default="DRAFT"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_ideas_user_id", "ideas", ["user_id"])
    op.create_index("idx_ideas_status", "ideas", ["status"])

    # ── reports ────────────────────────────────────────────────────────────────
    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("idea_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ideas.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_type", sa.Enum(
            "MARKET_RESEARCH", "COMPETITOR_ANALYSIS", "PRODUCT_MANAGER",
            "TECHNICAL_ARCHITECT", "DATABASE_ARCHITECT", "API_DESIGN",
            "UIUX", "ROADMAP", "MARKETING", "RISK_ANALYSIS",
            name="agent_type",
        ), nullable=False),
        sa.Column("status", sa.Enum("PENDING", "RUNNING", "COMPLETED", "FAILED", name="report_status"), nullable=False, server_default="PENDING"),
        sa.Column("output", postgresql.JSONB(), nullable=True),
        sa.Column("reasoning_summary", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("execution_time_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("idea_id", "agent_type", name="uq_report_idea_agent"),
    )
    op.create_index("idx_reports_idea_id", "reports", ["idea_id"])
    op.create_index("idx_reports_agent_type", "reports", ["agent_type"])
    op.create_index("idx_reports_status", "reports", ["status"])

    # ── agent_runs ─────────────────────────────────────────────────────────────
    op.create_table(
        "agent_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("report_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("reports.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_name", sa.String(100), nullable=False),
        sa.Column("input_snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("output_snapshot", postgresql.JSONB(), nullable=True),
        sa.Column("prompt_used", sa.Text(), nullable=True),
        sa.Column("model_used", sa.String(100), nullable=True),
        sa.Column("tokens_used", sa.Integer(), nullable=True),
        sa.Column("status", sa.Enum("PENDING", "RUNNING", "COMPLETED", "FAILED", name="report_status"), nullable=False, server_default="RUNNING"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_agent_runs_report_id", "agent_runs", ["report_id"])


def downgrade() -> None:
    """Drop all tables and enum types."""
    op.drop_table("agent_runs")
    op.drop_table("reports")
    op.drop_table("ideas")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS report_status")
    op.execute("DROP TYPE IF EXISTS agent_type")
    op.execute("DROP TYPE IF EXISTS idea_status")
