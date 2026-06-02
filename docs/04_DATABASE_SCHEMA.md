# FounderOS — Database Schema

**Version:** 1.0  
**Database:** PostgreSQL (Supabase Free Tier)  
**ORM:** SQLAlchemy 2.0

---

## 1. Entity Relationship Overview

```
users
  │
  └──< ideas (one user has many ideas)
          │
          └──< reports (one idea has many reports, one per agent)
                  │
                  └──< agent_runs (one report has many run attempts / trace entries)
```

---

## 2. Table Definitions

### 2.1 `users`

Stores registered user accounts.

```sql
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email       VARCHAR(255) NOT NULL UNIQUE,
    name        VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,   -- bcrypt hash, never plain text
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
```

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | UUID | PK | Auto-generated UUID v4 |
| email | VARCHAR(255) | NOT NULL, UNIQUE | Used as login identifier |
| name | VARCHAR(100) | NOT NULL | Display name |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt hash (cost=12) |
| is_active | BOOLEAN | DEFAULT TRUE | Soft disable support |
| created_at | TIMESTAMPTZ | NOT NULL | Auto-set on insert |
| updated_at | TIMESTAMPTZ | NOT NULL | Updated via trigger |

---

### 2.2 `ideas`

Stores startup ideas created by users.

```sql
CREATE TYPE idea_status AS ENUM (
    'DRAFT',        -- Created, not yet analyzed
    'PENDING',      -- Analysis queued
    'PROCESSING',   -- Agent pipeline running
    'COMPLETED',    -- All agents finished successfully
    'FAILED'        -- Pipeline failed (partial results may exist)
);

CREATE TABLE ideas (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title             VARCHAR(200) NOT NULL,        -- Startup name
    problem_statement TEXT NOT NULL,                -- What problem it solves
    target_audience   VARCHAR(500) NOT NULL,        -- Who it's for
    status            idea_status NOT NULL DEFAULT 'DRAFT',
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ideas_user_id ON ideas(user_id);
CREATE INDEX idx_ideas_status ON ideas(status);
```

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | UUID | PK | |
| user_id | UUID | FK → users.id | Cascades on user delete |
| title | VARCHAR(200) | NOT NULL | e.g., "AI Fitness App" |
| problem_statement | TEXT | NOT NULL | The core problem |
| target_audience | VARCHAR(500) | NOT NULL | Who the product serves |
| status | idea_status | NOT NULL | Pipeline state |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |

---

### 2.3 `reports`

Stores the output of each AI agent for a given idea. One row per agent per idea.

```sql
CREATE TYPE agent_type AS ENUM (
    'MARKET_RESEARCH',
    'COMPETITOR_ANALYSIS',
    'PRODUCT_MANAGER',
    'TECHNICAL_ARCHITECT',
    'DATABASE_ARCHITECT',
    'API_DESIGN',
    'UIUX',
    'ROADMAP',
    'MARKETING',
    'RISK_ANALYSIS'
);

CREATE TYPE report_status AS ENUM (
    'PENDING',      -- Not yet started
    'RUNNING',      -- Agent currently executing
    'COMPLETED',    -- Agent finished successfully
    'FAILED'        -- Agent encountered an error
);

CREATE TABLE reports (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idea_id             UUID NOT NULL REFERENCES ideas(id) ON DELETE CASCADE,
    agent_type          agent_type NOT NULL,
    status              report_status NOT NULL DEFAULT 'PENDING',
    output              JSONB,                          -- Agent's structured output
    reasoning_summary   TEXT,                          -- Brief summary of agent's reasoning
    error_message       TEXT,                          -- Populated if status=FAILED
    execution_time_ms   INTEGER,                       -- How long agent took
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(idea_id, agent_type)                        -- One report per agent per idea
);

CREATE INDEX idx_reports_idea_id ON reports(idea_id);
CREATE INDEX idx_reports_agent_type ON reports(agent_type);
CREATE INDEX idx_reports_status ON reports(status);
```

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | UUID | PK | |
| idea_id | UUID | FK → ideas.id | Cascades on idea delete |
| agent_type | agent_type | NOT NULL | Which agent produced this |
| status | report_status | NOT NULL | Current agent state |
| output | JSONB | NULLABLE | Structured JSON output |
| reasoning_summary | TEXT | NULLABLE | Human-readable summary |
| error_message | TEXT | NULLABLE | Error if FAILED |
| execution_time_ms | INTEGER | NULLABLE | Performance tracking |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |

---

### 2.4 `agent_runs`

Tracks every individual agent execution attempt. Powers the Agent Trace View feature.
Also captures retry attempts and partial outputs for debugging.

```sql
CREATE TABLE agent_runs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id       UUID NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    agent_name      VARCHAR(100) NOT NULL,              -- Human-readable agent name
    input_snapshot  JSONB NOT NULL,                     -- What the agent received
    output_snapshot JSONB,                              -- What the agent produced
    prompt_used     TEXT,                               -- Actual prompt sent to LLM
    model_used      VARCHAR(100),                       -- e.g. gemini-1.5-flash
    tokens_used     INTEGER,                            -- Token consumption
    status          report_status NOT NULL DEFAULT 'RUNNING',
    error_message   TEXT,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);

CREATE INDEX idx_agent_runs_report_id ON agent_runs(report_id);
```

| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| report_id | UUID | FK → reports.id |
| agent_name | VARCHAR(100) | e.g., "Market Research Agent" |
| input_snapshot | JSONB | State passed into this agent |
| output_snapshot | JSONB | State produced by this agent |
| prompt_used | TEXT | Full LLM prompt (for trace view) |
| model_used | VARCHAR(100) | Which LLM was used |
| tokens_used | INTEGER | For monitoring free tier limits |
| status | report_status | RUNNING → COMPLETED or FAILED |
| error_message | TEXT | If FAILED |
| started_at | TIMESTAMPTZ | |
| completed_at | TIMESTAMPTZ | NULL until finished |

---

## 3. SQLAlchemy Model Example

```python
# File: backend/app/models/idea.py
# Purpose: SQLAlchemy ORM model for the ideas table
# Maps Python class attributes to PostgreSQL columns

from sqlalchemy import Column, String, Text, Enum as SAEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, TimestampMixin
import enum

class IdeaStatus(str, enum.Enum):
    DRAFT      = "DRAFT"
    PENDING    = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED  = "COMPLETED"
    FAILED     = "FAILED"

class Idea(Base, TimestampMixin):
    """
    Description: ORM model representing a startup idea.
    Responsibilities:
      - Map to the 'ideas' PostgreSQL table
      - Define relationships to User and Report models
    """
    __tablename__ = "ideas"

    id               = Column(UUID(as_uuid=True), primary_key=True, ...)
    user_id          = Column(UUID(as_uuid=True), ForeignKey("users.id"), ...)
    title            = Column(String(200), nullable=False)
    problem_statement= Column(Text, nullable=False)
    target_audience  = Column(String(500), nullable=False)
    status           = Column(SAEnum(IdeaStatus), default=IdeaStatus.DRAFT)
```

---

## 4. Migration Strategy

Using **Alembic** for schema migrations:

```bash
# Generate migration
alembic revision --autogenerate -m "initial_schema"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

All migrations are committed to version control under `backend/alembic/versions/`.

---

## 5. Data Integrity Rules

| Rule | Implementation |
|---|---|
| No orphaned ideas | `ON DELETE CASCADE` from users → ideas |
| No orphaned reports | `ON DELETE CASCADE` from ideas → reports |
| One report per agent per idea | `UNIQUE(idea_id, agent_type)` constraint |
| No plain-text passwords | Application layer enforces bcrypt before INSERT |
| Timestamps always set | DEFAULT NOW() + updated via service layer |
| User data isolation | All queries filtered by `user_id` from JWT token |
