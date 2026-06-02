# FOUNDEROS — Architecture Blueprint
> "From Startup Idea to Execution Blueprint"
>
> **Status:** Pre-Development Architecture Review  
> **Version:** 1.0.0  
> **Date:** 2026-06-02  
> **Author:** Principal Software Architect

---

## TABLE OF CONTENTS

1. [Product Requirements Document (PRD)](#1-product-requirements-document)
2. [System Design](#2-system-design)
3. [Folder Structure](#3-folder-structure)
4. [Database Schema](#4-database-schema)
5. [API Design](#5-api-design)
6. [Agent Architecture](#6-agent-architecture)
7. [Sequence Diagrams](#7-sequence-diagrams)
8. [Development Roadmap](#8-development-roadmap)

---

# 1. PRODUCT REQUIREMENTS DOCUMENT

## 1.1 Product Vision

FounderOS transforms any startup idea into a complete, investor-ready execution blueprint using a pipeline of specialized AI agents. It eliminates weeks of research and planning by automating the work of an entire founding team — market researcher, product manager, architect, designer, and strategist — in minutes.

## 1.2 Problem Statement

First-time founders and solo entrepreneurs waste months attempting to structure their startup thinking before writing a single line of code. Existing tools (ChatGPT, Notion AI) require manual prompting and produce fragmented, unconnected outputs. There is no end-to-end AI system that takes a raw idea and returns a complete, structured startup plan.

## 1.3 Target Users

| Persona | Description |
|---|---|
| **Solo Founder** | Technical or non-technical individual validating an idea |
| **Student/Bootcamp Graduate** | Showcasing AI/product skills via portfolio |
| **Early-stage Team** | 1-3 person team needing structured planning |
| **AI/ML Engineer** | Portfolio project demonstrating multi-agent systems |

## 1.4 Feature Requirements

### Priority 0 — Must Have (Phase 1)

| ID | Feature | Description |
|---|---|---|
| F-001 | User Registration | Email + password signup |
| F-002 | User Login | JWT-based session |
| F-003 | Create Startup Idea | Name, problem, audience |
| F-004 | View Idea Dashboard | List of all user ideas |
| F-005 | Run Agent Pipeline | Trigger all 10 agents on an idea |
| F-006 | View Agent Output | Read each agent's generated report |
| F-007 | Agent Trace View | See which agent ran, its reasoning, and output |

### Priority 1 — Should Have (Phase 2)

| ID | Feature | Description |
|---|---|---|
| F-008 | Export to PDF | Full blueprint as downloadable PDF |
| F-009 | Export to Markdown | Full blueprint as downloadable .md |
| F-010 | Edit Idea | Update startup idea details |
| F-011 | Delete Idea | Remove idea and all reports |
| F-012 | Idea History | Re-visit past idea analyses |
| F-013 | RAG Knowledge Base | Agents enriched with startup methodologies |

### Priority 2 — Nice to Have (Phase 3)

| ID | Feature | Description |
|---|---|---|
| F-014 | Re-run Individual Agents | Re-generate a specific agent's output |
| F-015 | User Profile | Name, bio, avatar |
| F-016 | Shareable Blueprint Link | Public read-only URL for a blueprint |

## 1.5 Non-Functional Requirements

| Category | Requirement |
|---|---|
| **Performance** | Agent pipeline completes in < 120 seconds |
| **Reliability** | Graceful fallback from Gemini → OpenRouter |
| **Security** | Passwords hashed (bcrypt), JWT expiry, HTTPS only |
| **Code Quality** | Fully documented, modular, interview-ready |
| **Cost** | 100% free-tier technologies only |
| **Deployability** | Frontend on Vercel, Backend on Render, DB on Supabase |

---

# 2. SYSTEM DESIGN

## 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER (Browser)                           │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FRONTEND (Vercel)                             │
│   Next.js 15 · TypeScript · Tailwind · ShadCN · Zustand        │
│                                                                 │
│   Pages: Login · Register · Dashboard · Workspace · Trace      │
└───────────────────────────┬─────────────────────────────────────┘
                            │ REST + WebSocket
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   BACKEND (Render)                              │
│   FastAPI · Python · SQLAlchemy · Pydantic                     │
│                                                                 │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │  Auth API   │  │  Ideas API   │  │     Agents API         │ │
│  └─────────────┘  └──────────────┘  └────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              AGENT PIPELINE (LangGraph)                   │  │
│  │  [Market] → [Competitor] → [PM] → [Architect] → [DB]     │  │
│  │  → [API] → [UX] → [Roadmap] → [Marketing] → [Risk]       │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────┐    ┌──────────────────────────────┐   │
│  │   RAG Service        │    │   AI Client (Gemini/ORouter) │   │
│  │   ChromaDB +         │    │   Retry logic + Fallback     │   │
│  │   SentenceTransform. │    └──────────────────────────────┘   │
│  └──────────────────────┘                                       │
└───────────┬───────────────────────┬─────────────────────────────┘
            │ SQLAlchemy            │ ChromaDB (local)
            ▼                      ▼
┌───────────────────┐   ┌──────────────────────┐
│  PostgreSQL DB    │   │  ChromaDB Vector DB   │
│  (Supabase)       │   │  (Render local disk)  │
└───────────────────┘   └──────────────────────┘
```

## 2.2 Component Descriptions

### Frontend
- **Next.js 15 App Router** — file-based routing, server/client components
- **Zustand** — global state for auth session and active idea
- **React Query** — server state, caching, background refetching
- **ShadCN UI** — accessible, unstyled component primitives
- **Tailwind CSS** — utility-first styling

### Backend
- **FastAPI** — async Python API framework with auto-generated OpenAPI docs
- **SQLAlchemy** — ORM for PostgreSQL; models defined as Python classes
- **Pydantic v2** — request/response validation schemas
- **LangGraph** — stateful multi-agent orchestration graph
- **ChromaDB** — local vector store for RAG knowledge base
- **Sentence Transformers** — free, local embedding model (`all-MiniLM-L6-v2`)

### AI Layer
- **Primary:** Google Gemini 2.0 Flash (free tier via `google-generativeai`)
- **Fallback:** OpenRouter free models (Mistral, Llama via REST)
- **Client wrapper** handles retry, rate-limit detection, and automatic fallback

### WebSocket
- FastAPI native WebSocket at `/ws/agents/{run_id}`
- Pushes real-time agent progress updates to frontend
- Frontend displays live agent trace while pipeline runs

---

# 3. FOLDER STRUCTURE

## 3.1 Repository Layout

```
FOUNDEROS/
├── frontend/                  # Next.js 15 application
├── backend/                   # FastAPI application
├── docs/                      # Architecture docs, diagrams
│   └── ARCHITECTURE.md        # ← This file
└── README.md
```

## 3.2 Frontend Folder Structure

```
frontend/
├── public/
│   └── logo.svg
├── src/
│   ├── app/                          # Next.js App Router
│   │   ├── layout.tsx                # Root layout (fonts, providers)
│   │   ├── page.tsx                  # Landing page
│   │   ├── (auth)/                   # Auth route group (no sidebar)
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── register/
│   │   │       └── page.tsx
│   │   └── (app)/                    # Authenticated route group
│   │       ├── layout.tsx            # App layout (sidebar + navbar)
│   │       ├── dashboard/
│   │       │   └── page.tsx          # Idea list
│   │       └── ideas/
│   │           └── [id]/
│   │               ├── page.tsx      # Idea workspace (run agents)
│   │               └── trace/
│   │                   └── page.tsx  # Agent trace viewer
│   │
│   ├── components/
│   │   ├── ui/                       # ShadCN auto-generated components
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   └── RegisterForm.tsx
│   │   ├── dashboard/
│   │   │   ├── IdeaCard.tsx
│   │   │   ├── IdeaGrid.tsx
│   │   │   └── CreateIdeaDialog.tsx
│   │   ├── workspace/
│   │   │   ├── IdeaHeader.tsx
│   │   │   ├── AgentPipelinePanel.tsx
│   │   │   ├── AgentReportCard.tsx
│   │   │   └── ExportButtons.tsx
│   │   └── trace/
│   │       ├── AgentTraceList.tsx
│   │       └── AgentTraceItem.tsx
│   │
│   ├── lib/
│   │   ├── api/
│   │   │   ├── client.ts             # Axios instance with interceptors
│   │   │   ├── auth.api.ts           # Auth endpoint calls
│   │   │   ├── ideas.api.ts          # Ideas endpoint calls
│   │   │   └── agents.api.ts         # Agent run/status calls
│   │   ├── auth/
│   │   │   └── session.ts            # Token storage helpers
│   │   └── utils/
│   │       ├── cn.ts                 # Tailwind class merge util
│   │       └── format.ts             # Date, text formatters
│   │
│   ├── stores/
│   │   ├── auth.store.ts             # Zustand: user session state
│   │   └── idea.store.ts             # Zustand: active idea state
│   │
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useIdeas.ts
│   │   ├── useAgentRun.ts            # React Query + WebSocket combo
│   │   └── useAgentTrace.ts
│   │
│   └── types/
│       ├── auth.types.ts
│       ├── idea.types.ts
│       └── agent.types.ts
│
├── .env.local
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

## 3.3 Backend Folder Structure

```
backend/
├── app/
│   ├── main.py                        # FastAPI app factory, router registration
│   ├── config.py                      # Settings (env vars via Pydantic BaseSettings)
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── router.py              # Aggregates all v1 routers
│   │       ├── auth/
│   │       │   ├── router.py          # /auth endpoints
│   │       │   ├── dependencies.py    # get_current_user dep
│   │       │   └── schemas.py         # LoginRequest, RegisterRequest, TokenResponse
│   │       ├── ideas/
│   │       │   ├── router.py          # /ideas endpoints
│   │       │   └── schemas.py         # IdeaCreate, IdeaUpdate, IdeaResponse
│   │       ├── agents/
│   │       │   ├── router.py          # /agents endpoints
│   │       │   └── schemas.py         # RunRequest, RunStatusResponse
│   │       └── reports/
│   │           ├── router.py          # /reports endpoints
│   │           └── schemas.py         # ReportResponse, ExportResponse
│   │
│   ├── agents/                        # LangGraph agent definitions
│   │   ├── pipeline.py                # LangGraph graph builder & state definition
│   │   ├── state.py                   # AgentPipelineState TypedDict
│   │   ├── base_agent.py              # Abstract base class for all agents
│   │   ├── market_research/
│   │   │   ├── agent.py               # MarketResearchAgent class
│   │   │   └── prompts.py             # System + user prompt templates
│   │   ├── competitor_analysis/
│   │   │   ├── agent.py
│   │   │   └── prompts.py
│   │   ├── product_manager/
│   │   │   ├── agent.py
│   │   │   └── prompts.py
│   │   ├── technical_architect/
│   │   │   ├── agent.py
│   │   │   └── prompts.py
│   │   ├── database_architect/
│   │   │   ├── agent.py
│   │   │   └── prompts.py
│   │   ├── api_design/
│   │   │   ├── agent.py
│   │   │   └── prompts.py
│   │   ├── ui_ux/
│   │   │   ├── agent.py
│   │   │   └── prompts.py
│   │   ├── roadmap/
│   │   │   ├── agent.py
│   │   │   └── prompts.py
│   │   ├── marketing/
│   │   │   ├── agent.py
│   │   │   └── prompts.py
│   │   └── risk_analysis/
│   │       ├── agent.py
│   │       └── prompts.py
│   │
│   ├── core/
│   │   ├── database.py                # SQLAlchemy engine + session factory
│   │   ├── security.py                # Password hashing, JWT encode/decode
│   │   ├── exceptions.py              # Custom exception classes + handlers
│   │   └── websocket_manager.py       # WS connection manager for live updates
│   │
│   ├── models/                        # SQLAlchemy ORM models (DB tables)
│   │   ├── base.py                    # Declarative base + shared columns
│   │   ├── user.py                    # User model
│   │   ├── startup_idea.py            # StartupIdea model
│   │   ├── agent_run.py               # AgentRun model (pipeline run)
│   │   ├── agent_report.py            # AgentReport model (per-agent output)
│   │   └── startup_blueprint.py       # StartupBlueprint model (final export)
│   │
│   ├── services/                      # Business logic layer
│   │   ├── auth_service.py            # Register, login, token management
│   │   ├── idea_service.py            # CRUD for ideas
│   │   ├── agent_service.py           # Trigger pipeline, poll status
│   │   └── export_service.py          # PDF + Markdown generation
│   │
│   ├── rag/
│   │   ├── chroma_client.py           # ChromaDB init + collection management
│   │   ├── embedder.py                # SentenceTransformer wrapper
│   │   ├── retriever.py               # Query vector DB, return context chunks
│   │   └── seed_knowledge.py          # CLI script to seed knowledge base
│   │
│   └── utils/
│       ├── ai_client.py               # Gemini + OpenRouter wrapper with fallback
│       ├── logger.py                  # Structured logging setup
│       └── response.py                # Standard API response helpers
│
├── migrations/                        # Alembic DB migrations
│   ├── env.py
│   └── versions/
│
├── tests/
│   ├── test_auth.py
│   ├── test_ideas.py
│   └── test_agents.py
│
├── scripts/
│   └── seed_rag.py                    # Run once to populate ChromaDB
│
├── .env
├── alembic.ini
├── requirements.txt
└── Dockerfile
```

---

# 4. DATABASE SCHEMA

## 4.1 Entity Overview

| Table | Purpose |
|---|---|
| `users` | Registered user accounts |
| `startup_ideas` | User-created startup ideas |
| `agent_runs` | One record per full pipeline execution |
| `agent_reports` | One record per agent per run (10 reports per run) |
| `startup_blueprints` | Final assembled blueprint (all reports combined) |

## 4.2 Entity Relationship Diagram

```
users (1) ──────────── (many) startup_ideas
startup_ideas (1) ────── (many) agent_runs
agent_runs (1) ─────────── (many) agent_reports
agent_runs (1) ──────────── (0..1) startup_blueprints
```

## 4.3 SQL Schema (PostgreSQL)

```sql
-- ============================================================
-- TABLE: users
-- Purpose: Stores registered user accounts
-- ============================================================
CREATE TABLE users (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255)    NOT NULL UNIQUE,
    hashed_password VARCHAR(255)    NOT NULL,
    full_name       VARCHAR(255),
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);


-- ============================================================
-- TABLE: startup_ideas
-- Purpose: Stores user-created startup ideas
-- ============================================================
CREATE TABLE startup_ideas (
    id                UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID            NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name              VARCHAR(255)    NOT NULL,
    problem_statement TEXT            NOT NULL,
    target_audience   TEXT            NOT NULL,
    additional_context TEXT,
    status            VARCHAR(50)     NOT NULL DEFAULT 'draft',
    -- status values: 'draft' | 'processing' | 'completed' | 'failed'
    created_at        TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_startup_ideas_user_id ON startup_ideas(user_id);
CREATE INDEX idx_startup_ideas_status  ON startup_ideas(status);


-- ============================================================
-- TABLE: agent_runs
-- Purpose: Tracks each full pipeline execution for an idea
-- ============================================================
CREATE TABLE agent_runs (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    idea_id         UUID            NOT NULL REFERENCES startup_ideas(id) ON DELETE CASCADE,
    status          VARCHAR(50)     NOT NULL DEFAULT 'pending',
    -- status values: 'pending' | 'running' | 'completed' | 'failed'
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    error_message   TEXT,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_agent_runs_idea_id ON agent_runs(idea_id);
CREATE INDEX idx_agent_runs_status  ON agent_runs(status);


-- ============================================================
-- TABLE: agent_reports
-- Purpose: Stores each individual agent's output within a run
-- ============================================================
CREATE TABLE agent_reports (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id          UUID            NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE,
    agent_name      VARCHAR(100)    NOT NULL,
    -- agent_name values (exact):
    -- 'market_research' | 'competitor_analysis' | 'product_manager'
    -- 'technical_architect' | 'database_architect' | 'api_design'
    -- 'ui_ux' | 'roadmap' | 'marketing' | 'risk_analysis'
    status          VARCHAR(50)     NOT NULL DEFAULT 'pending',
    -- status values: 'pending' | 'running' | 'completed' | 'failed'
    output          JSONB,          -- Structured agent output
    reasoning       TEXT,           -- Agent's reasoning summary (trace)
    tokens_used     INTEGER,        -- Token count for cost tracking
    duration_ms     INTEGER,        -- Execution time in milliseconds
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    error_message   TEXT,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_agent_reports_run_id     ON agent_reports(run_id);
CREATE INDEX idx_agent_reports_agent_name ON agent_reports(agent_name);


-- ============================================================
-- TABLE: startup_blueprints
-- Purpose: Final assembled blueprint combining all agent outputs
-- ============================================================
CREATE TABLE startup_blueprints (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id          UUID            NOT NULL UNIQUE REFERENCES agent_runs(id) ON DELETE CASCADE,
    idea_id         UUID            NOT NULL REFERENCES startup_ideas(id) ON DELETE CASCADE,
    content_md      TEXT,           -- Full markdown export
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_startup_blueprints_idea_id ON startup_blueprints(idea_id);
```

## 4.4 JSONB Output Structure per Agent

Each `agent_reports.output` column stores structured JSON. Examples:

```json
// market_research output
{
  "industry_overview": "...",
  "market_trends": ["trend1", "trend2"],
  "market_opportunities": ["opp1", "opp2"],
  "potential_demand": "..."
}

// competitor_analysis output
{
  "competitors": [
    {
      "name": "CompanyX",
      "strengths": ["..."],
      "weaknesses": ["..."]
    }
  ],
  "market_gaps": ["gap1", "gap2"]
}

// product_manager output
{
  "product_vision": "...",
  "prd_summary": "...",
  "features": ["feature1", "feature2"],
  "user_stories": [
    {
      "as_a": "user",
      "i_want": "...",
      "so_that": "...",
      "acceptance_criteria": ["..."]
    }
  ]
}
```

---

# 5. API DESIGN

## 5.1 Base URL

```
Development:  http://localhost:8000/api/v1
Production:   https://founderos-api.onrender.com/api/v1
```

## 5.2 Authentication Endpoints

### POST /auth/register
**Purpose:** Create a new user account

Request:
```json
{
  "email": "founder@example.com",
  "password": "SecurePass123!",
  "full_name": "Jane Doe"
}
```

Response `201`:
```json
{
  "success": true,
  "data": {
    "user": { "id": "uuid", "email": "founder@example.com", "full_name": "Jane Doe" },
    "access_token": "eyJhbGci...",
    "token_type": "bearer"
  }
}
```

---

### POST /auth/login
**Purpose:** Authenticate and receive access token

Request:
```json
{
  "email": "founder@example.com",
  "password": "SecurePass123!"
}
```

Response `200`:
```json
{
  "success": true,
  "data": {
    "user": { "id": "uuid", "email": "founder@example.com", "full_name": "Jane Doe" },
    "access_token": "eyJhbGci...",
    "token_type": "bearer"
  }
}
```

---

### GET /auth/me
**Purpose:** Get current authenticated user  
**Auth:** Bearer token required

Response `200`:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "founder@example.com",
    "full_name": "Jane Doe",
    "created_at": "2026-06-02T10:00:00Z"
  }
}
```

---

## 5.3 Ideas Endpoints

### POST /ideas
**Purpose:** Create a new startup idea  
**Auth:** Required

Request:
```json
{
  "name": "AI Fitness App",
  "problem_statement": "People struggle to stay consistent with fitness routines without personalized guidance.",
  "target_audience": "Busy professionals aged 25-40",
  "additional_context": "Focused on 10-minute daily workouts"
}
```

Response `201`:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "AI Fitness App",
    "problem_statement": "...",
    "target_audience": "...",
    "status": "draft",
    "created_at": "2026-06-02T10:00:00Z"
  }
}
```

---

### GET /ideas
**Purpose:** List all ideas for current user  
**Auth:** Required

Response `200`:
```json
{
  "success": true,
  "data": {
    "ideas": [...],
    "total": 5
  }
}
```

---

### GET /ideas/{idea_id}
**Purpose:** Get a single idea with its latest report  
**Auth:** Required

Response `200`:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "AI Fitness App",
    "status": "completed",
    "latest_run_id": "uuid",
    "created_at": "..."
  }
}
```

---

### PUT /ideas/{idea_id}
**Purpose:** Update idea details  
**Auth:** Required

Request:
```json
{
  "name": "AI Fitness Coach",
  "problem_statement": "Updated problem..."
}
```

---

### DELETE /ideas/{idea_id}
**Purpose:** Delete idea and all associated reports  
**Auth:** Required

Response `200`:
```json
{ "success": true, "message": "Idea deleted successfully" }
```

---

## 5.4 Agent Run Endpoints

### POST /agents/run/{idea_id}
**Purpose:** Start the full 10-agent pipeline for an idea  
**Auth:** Required

Response `202`:
```json
{
  "success": true,
  "data": {
    "run_id": "uuid",
    "status": "pending",
    "message": "Pipeline started. Connect to WebSocket for live updates."
  }
}
```

---

### GET /agents/run/{run_id}/status
**Purpose:** Poll pipeline run status  
**Auth:** Required

Response `200`:
```json
{
  "success": true,
  "data": {
    "run_id": "uuid",
    "status": "running",
    "current_agent": "product_manager",
    "completed_agents": ["market_research", "competitor_analysis"],
    "started_at": "...",
    "completed_at": null
  }
}
```

---

### GET /agents/run/{run_id}/trace
**Purpose:** Get full agent trace (all agent outputs + reasoning)  
**Auth:** Required

Response `200`:
```json
{
  "success": true,
  "data": {
    "run_id": "uuid",
    "agents": [
      {
        "agent_name": "market_research",
        "status": "completed",
        "reasoning": "I analyzed the fitness app market by...",
        "output": { "industry_overview": "...", ... },
        "duration_ms": 4200,
        "completed_at": "..."
      }
    ]
  }
}
```

---

## 5.5 Reports Endpoints

### GET /reports/{idea_id}
**Purpose:** Get all reports for an idea  
**Auth:** Required

Response `200`:
```json
{
  "success": true,
  "data": {
    "idea_id": "uuid",
    "run_id": "uuid",
    "reports": {
      "market_research": { ... },
      "competitor_analysis": { ... },
      ...
    }
  }
}
```

---

### GET /reports/{idea_id}/export/pdf
**Purpose:** Download full blueprint as PDF  
**Auth:** Required  
**Response:** `application/pdf` binary file

---

### GET /reports/{idea_id}/export/markdown
**Purpose:** Download full blueprint as Markdown  
**Auth:** Required  
**Response:** `text/markdown` file download

---

## 5.6 WebSocket

### WS /ws/agents/{run_id}
**Purpose:** Real-time agent pipeline progress updates

Message format (server → client):
```json
{
  "event": "agent_started",
  "agent": "product_manager",
  "timestamp": "2026-06-02T10:01:30Z"
}
```
```json
{
  "event": "agent_completed",
  "agent": "product_manager",
  "output_preview": "Generated PRD with 12 features...",
  "duration_ms": 5100,
  "timestamp": "2026-06-02T10:01:35Z"
}
```
```json
{
  "event": "pipeline_completed",
  "run_id": "uuid",
  "total_duration_ms": 48200,
  "timestamp": "2026-06-02T10:02:18Z"
}
```

---

# 6. AGENT ARCHITECTURE

## 6.1 LangGraph State

All agents share a single typed state dictionary that flows through the pipeline. Each agent reads from it and adds its output.

```python
class AgentPipelineState(TypedDict):
    # Input
    idea_id:                    str
    run_id:                     str
    startup_name:               str
    problem_statement:          str
    target_audience:            str
    additional_context:         str

    # Agent Outputs (populated as pipeline progresses)
    market_research_output:     Optional[dict]
    competitor_analysis_output: Optional[dict]
    product_manager_output:     Optional[dict]
    technical_architect_output: Optional[dict]
    database_architect_output:  Optional[dict]
    api_design_output:          Optional[dict]
    ui_ux_output:               Optional[dict]
    roadmap_output:             Optional[dict]
    marketing_output:           Optional[dict]
    risk_analysis_output:       Optional[dict]

    # Metadata
    current_agent:              str
    errors:                     list[str]
    completed_agents:           list[str]
```

## 6.2 Agent Pipeline Graph

```
[START]
  │
  ▼
┌─────────────────────┐
│  market_research    │  Input: idea fields
│                     │  Output: industry overview, trends, demand
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ competitor_analysis │  Input: idea + market_research_output
│                     │  Output: competitors, gaps
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  product_manager    │  Input: idea + market + competitors
│                     │  Output: PRD, features, user stories
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ technical_architect │  Input: PRD output
│                     │  Output: architecture, tech stack, scalability
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ database_architect  │  Input: PRD + tech architecture
│                     │  Output: entities, relationships, SQL schema
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│    api_design       │  Input: PRD + DB schema
│                     │  Output: REST endpoints, request/response examples
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│      ui_ux          │  Input: PRD + user stories
│                     │  Output: screens, components, user flows
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│      roadmap        │  Input: all previous outputs
│                     │  Output: week-by-week MVP plan
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│     marketing       │  Input: idea + market + PRD
│                     │  Output: ICP, channels, launch strategy
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   risk_analysis     │  Input: all previous outputs
│                     │  Output: risks, assumptions, mitigations
└─────────┬───────────┘
          │
          ▼
[END] → Assemble Blueprint → Save to DB
```

## 6.3 Agent Base Class Contract

Every agent implements:

```python
class BaseAgent(ABC):
    name: str                  # Unique agent identifier
    description: str           # Human-readable description

    def build_prompt(state: AgentPipelineState) -> str
        # Constructs the LLM prompt using state data + RAG context

    async def run(state: AgentPipelineState) -> AgentPipelineState
        # Calls LLM, parses response, updates state, saves to DB

    def parse_response(raw: str) -> dict
        # Converts LLM text output to structured dict
```

## 6.4 AI Client with Fallback

```
Request
  │
  ▼
┌─────────────────────────────────┐
│    Gemini 2.0 Flash (Primary)   │
│    google-generativeai SDK      │
└──────────────┬──────────────────┘
               │ 429 / Error?
               ▼
┌─────────────────────────────────┐
│  OpenRouter Free (Fallback)     │
│  Model: mistralai/mistral-7b    │
│  REST API call                  │
└─────────────────────────────────┘
```

## 6.5 RAG Integration per Agent

```
Agent.build_prompt(state)
  │
  ├── 1. Extract query from state (e.g., "fitness app market research")
  │
  ├── 2. retriever.query(query, n_results=3)
  │        └── SentenceTransformer.encode(query) → ChromaDB.query()
  │            └── Returns top 3 relevant knowledge chunks
  │
  ├── 3. Inject chunks into prompt as "RELEVANT CONTEXT:"
  │
  └── 4. Return enriched prompt → LLM call
```

Knowledge base is seeded once with: Lean Startup methodology, Product Development frameworks, Go-to-Market playbooks, technical architecture patterns.

---

# 7. SEQUENCE DIAGRAMS

## 7.1 User Registration

```
Browser          Frontend         Backend           Database
   │                │                │                  │
   │──POST /register─────────────────►│                  │
   │                │                │──hash password───►│
   │                │                │──INSERT user──────►│
   │                │                │◄──user record─────│
   │                │                │──generate JWT      │
   │◄──201 {token}──────────────────│                  │
   │                │                │                  │
```

## 7.2 Create Idea & Run Pipeline

```
Browser     Frontend    Backend API    AgentService    LangGraph    DB      WS
   │           │             │               │              │         │       │
   │──POST /ideas────────────►│               │              │         │       │
   │           │             │──INSERT idea──────────────────────────►│       │
   │◄──201 {idea}────────────│               │              │         │       │
   │           │             │               │              │         │       │
   │──POST /agents/run───────►│               │              │         │       │
   │           │             │──create run───────────────────────────►│       │
   │◄──202 {run_id}──────────│               │              │         │       │
   │           │             │               │              │         │       │
   │──WS connect────────────────────────────────────────────────────────────►│
   │           │             │──trigger_async►│              │         │       │
   │           │             │               │──START GRAPH─►│         │       │
   │           │             │               │              │──agent1──►│      │
   │◄──WS: agent_started─────────────────────────────────────────────────────│
   │           │             │               │              │◄─result──│       │
   │◄──WS: agent_completed───────────────────────────────────────────────────│
   │           │  [repeats for each of 10 agents]           │         │       │
   │◄──WS: pipeline_completed────────────────────────────────────────────────│
   │           │             │               │              │──blueprint────►│ │
```

## 7.3 Export to PDF

```
Browser     Frontend    Backend     ExportService    DB
   │           │            │              │           │
   │──GET /reports/{id}/export/pdf─────────►│           │
   │           │            │──fetch all reports───────►│
   │           │            │◄─────reports─────────────│
   │           │            │──render_markdown          │
   │           │            │──convert_to_pdf           │
   │◄──200 PDF binary────────│              │           │
```

---

# 8. DEVELOPMENT ROADMAP

## Overview

| Phase | Name | Duration | Goal |
|---|---|---|---|
| Phase 1 | Foundation | Week 1-2 | Auth, DB, basic CRUD, project scaffolding |
| Phase 2 | Core Agents | Week 3-5 | All 10 agents running, pipeline working |
| Phase 3 | Advanced Features | Week 6-7 | RAG, export, agent trace UI |
| Phase 4 | Polish & Deploy | Week 8 | Testing, Vercel + Render deploy |

---

## Phase 1 — Foundation (Week 1–2)

### Week 1: Project Setup & Authentication
- [ ] Initialize Next.js 15 frontend with TypeScript + Tailwind + ShadCN
- [ ] Initialize FastAPI backend with folder structure
- [ ] Configure PostgreSQL on Supabase (free tier)
- [ ] Set up SQLAlchemy + Alembic migrations
- [ ] Implement User model + migrations
- [ ] Implement POST /auth/register and POST /auth/login
- [ ] Implement JWT generation + verification
- [ ] Implement `get_current_user` FastAPI dependency
- [ ] Build Login and Register pages (frontend)
- [ ] Connect frontend auth to backend via React Query

### Week 2: Dashboard & Idea CRUD
- [ ] Implement StartupIdea model + migrations
- [ ] Implement all /ideas endpoints (CRUD)
- [ ] Build Dashboard page (idea grid with cards)
- [ ] Build Create Idea dialog/form
- [ ] Build Edit Idea and Delete Idea
- [ ] Implement Zustand store for auth + ideas
- [ ] Set up Axios client with JWT interceptor

---

## Phase 2 — Core Agents (Week 3–5)

### Week 3: Agent Infrastructure
- [ ] Implement `ai_client.py` (Gemini + OpenRouter fallback)
- [ ] Implement `BaseAgent` abstract class
- [ ] Define `AgentPipelineState` TypedDict
- [ ] Set up LangGraph pipeline scaffold
- [ ] Implement AgentRun + AgentReport models + migrations
- [ ] Implement WebSocket manager
- [ ] Implement POST /agents/run/{idea_id} endpoint
- [ ] Implement async pipeline trigger (FastAPI BackgroundTasks)

### Week 4: Agents 1–5
- [ ] MarketResearchAgent (prompts + parser + LangGraph node)
- [ ] CompetitorAnalysisAgent
- [ ] ProductManagerAgent
- [ ] TechnicalArchitectAgent
- [ ] DatabaseArchitectAgent
- [ ] Wire agents into sequential pipeline
- [ ] Save each agent output to `agent_reports` table

### Week 5: Agents 6–10 + Workspace UI
- [ ] APIDesignAgent
- [ ] UIUXAgent
- [ ] RoadmapAgent
- [ ] MarketingAgent
- [ ] RiskAnalysisAgent
- [ ] Assemble `StartupBlueprint` on pipeline completion
- [ ] Build Idea Workspace page (frontend)
- [ ] Build live WebSocket progress tracker in frontend
- [ ] Build AgentReportCard components (collapsible, per agent)

---

## Phase 3 — Advanced Features (Week 6–7)

### Week 6: RAG Knowledge Base
- [ ] Set up ChromaDB client
- [ ] Implement SentenceTransformer embedder
- [ ] Implement `retriever.py`
- [ ] Write `seed_knowledge.py` script (Lean Startup, agile frameworks, etc.)
- [ ] Run seed script, verify ChromaDB populated
- [ ] Integrate RAG context into each agent's `build_prompt()`

### Week 7: Export + Agent Trace
- [ ] Implement Markdown export (assemble all reports → .md)
- [ ] Implement PDF export (markdown → PDF via `weasyprint` or `reportlab`)
- [ ] Build Export Buttons component (frontend)
- [ ] Build Agent Trace View page (frontend)
- [ ] Wire GET /agents/run/{run_id}/trace endpoint
- [ ] Display reasoning + duration + output for each agent

---

## Phase 4 — Polish & Deploy (Week 8)

### Testing
- [ ] Write pytest tests for auth endpoints
- [ ] Write pytest tests for idea CRUD
- [ ] Write pytest tests for agent pipeline (mock LLM)
- [ ] Manual end-to-end test with real idea

### Deployment
- [ ] Configure Render for FastAPI backend (free tier)
- [ ] Add environment variables to Render dashboard
- [ ] Configure Vercel for Next.js frontend (free tier)
- [ ] Add environment variables to Vercel dashboard
- [ ] Run Alembic migrations on production Supabase DB
- [ ] Verify full flow in production

### Final Polish
- [ ] Error states and loading states (frontend)
- [ ] 404 and empty state pages
- [ ] Mobile responsive layout check
- [ ] README.md with setup instructions
- [ ] Demo video / screenshots for portfolio

---

## Environment Variables Reference

### Backend (.env)
```
DATABASE_URL=postgresql://user:pass@db.supabase.co:5432/postgres
SECRET_KEY=your-super-secret-jwt-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
GEMINI_API_KEY=your-gemini-api-key
OPENROUTER_API_KEY=your-openrouter-api-key
CHROMA_PERSIST_DIR=./chroma_data
ENVIRONMENT=development
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

---

## Free Services Setup Checklist

| Service | URL | Action |
|---|---|---|
| **Supabase** (PostgreSQL) | supabase.com | Create project → copy DATABASE_URL |
| **Google AI Studio** (Gemini) | aistudio.google.com | Create API key → copy to .env |
| **OpenRouter** (Fallback LLM) | openrouter.ai | Sign up free → get API key |
| **Vercel** (Frontend) | vercel.com | Connect GitHub → deploy frontend/ |
| **Render** (Backend) | render.com | Connect GitHub → deploy backend/ |

---

*End of Architecture Document — Awaiting approval before code generation begins.*
