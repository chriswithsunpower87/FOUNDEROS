"""Initial schema — users, ideas, reports, agent_runs

Revision ID: 001
Revises:
Create Date: 2026-06-02
"""

from alembic import op

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables using raw SQL to avoid SQLAlchemy enum double-creation."""

    op.execute("""
        -- ── Enum types ──────────────────────────────────────────────────────────
        CREATE TYPE idea_status AS ENUM (
            'DRAFT', 'PENDING', 'PROCESSING', 'COMPLETED', 'FAILED'
        );

        CREATE TYPE agent_type AS ENUM (
            'MARKET_RESEARCH', 'COMPETITOR_ANALYSIS', 'PRODUCT_MANAGER',
            'TECHNICAL_ARCHITECT', 'DATABASE_ARCHITECT', 'API_DESIGN',
            'UIUX', 'ROADMAP', 'MARKETING', 'RISK_ANALYSIS'
        );

        CREATE TYPE report_status AS ENUM (
            'PENDING', 'RUNNING', 'COMPLETED', 'FAILED'
        );

        -- ── users ────────────────────────────────────────────────────────────────
        CREATE TABLE users (
            id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email       VARCHAR(255) NOT NULL UNIQUE,
            name        VARCHAR(100) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            is_active   BOOLEAN NOT NULL DEFAULT TRUE,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        CREATE INDEX idx_users_email ON users(email);

        -- ── ideas ────────────────────────────────────────────────────────────────
        CREATE TABLE ideas (
            id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id           UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title             VARCHAR(200) NOT NULL,
            problem_statement TEXT NOT NULL,
            target_audience   VARCHAR(500) NOT NULL,
            status            idea_status NOT NULL DEFAULT 'DRAFT',
            created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        CREATE INDEX idx_ideas_user_id ON ideas(user_id);
        CREATE INDEX idx_ideas_status ON ideas(status);

        -- ── reports ──────────────────────────────────────────────────────────────
        CREATE TABLE reports (
            id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            idea_id             UUID NOT NULL REFERENCES ideas(id) ON DELETE CASCADE,
            agent_type          agent_type NOT NULL,
            status              report_status NOT NULL DEFAULT 'PENDING',
            output              JSONB,
            reasoning_summary   TEXT,
            error_message       TEXT,
            execution_time_ms   INTEGER,
            created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE(idea_id, agent_type)
        );
        CREATE INDEX idx_reports_idea_id ON reports(idea_id);
        CREATE INDEX idx_reports_agent_type ON reports(agent_type);
        CREATE INDEX idx_reports_status ON reports(status);

        -- ── agent_runs ───────────────────────────────────────────────────────────
        CREATE TABLE agent_runs (
            id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            report_id       UUID NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
            agent_name      VARCHAR(100) NOT NULL,
            input_snapshot  JSONB NOT NULL,
            output_snapshot JSONB,
            prompt_used     TEXT,
            model_used      VARCHAR(100),
            tokens_used     INTEGER,
            status          report_status NOT NULL DEFAULT 'RUNNING',
            error_message   TEXT,
            started_at      TIMESTAMPTZ NOT NULL,
            completed_at    TIMESTAMPTZ
        );
        CREATE INDEX idx_agent_runs_report_id ON agent_runs(report_id);
    """)


def downgrade() -> None:
    """Drop all tables and enum types."""
    op.execute("""
        DROP TABLE IF EXISTS agent_runs;
        DROP TABLE IF EXISTS reports;
        DROP TABLE IF EXISTS ideas;
        DROP TABLE IF EXISTS users;
        DROP TYPE IF EXISTS report_status;
        DROP TYPE IF EXISTS agent_type;
        DROP TYPE IF EXISTS idea_status;
    """)
