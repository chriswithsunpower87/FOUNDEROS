# FounderOS 🚀

> **"From Startup Idea to Execution Blueprint"**

A production-grade, AI-powered startup planning platform. Enter any idea — FounderOS deploys 11 specialized AI agents in parallel to generate a complete startup blueprint in minutes.

[![CI](https://github.com/YOUR_GITHUB_USERNAME/FOUNDEROS/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_GITHUB_USERNAME/FOUNDEROS/actions)
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-orange)](https://langchain-ai.github.io/langgraph)
[![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)](./docker-compose.yml)

---

## Live Demo

🌐 **[founderos.vercel.app](https://founderos.vercel.app)** ← try it here

---

## What It Does

You type: *"AI fitness app for busy professionals"*

FounderOS runs 11 AI specialist agents in parallel and produces:

| Agent | Output |
|---|---|
| 📊 Market Research | Industry overview, TAM/SAM/SOM, market trends |
| 🔍 Competitor Analysis | Competitor matrix, market gaps, differentiation |
| 📋 Product Manager | PRD, user stories, acceptance criteria |
| 🏗️ Technical Architect | System design, tech stack recommendations |
| 🗄️ Database Architect | Entity-relationship model, SQL schema |
| 🔌 API Design | REST endpoint specs with request/response examples |
| 🎨 UI/UX Designer | Screen designs, component hierarchy, color palette |
| 🗺️ Roadmap | Week-by-week MVP execution plan |
| 📣 Go-To-Market | ICP, marketing channels, launch strategy |
| ⚠️ Risk Analysis | Risk matrix with severity + mitigation strategies |
| 💰 Revenue & Cost | Revenue models, pricing tiers, unit economics, projections |

**Export** the full blueprint as PDF or Markdown.  
**Share** via a public URL — no login required to view.  
**Version history** — every re-analysis is preserved and browsable.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Next.js 15 Frontend                          │
│   React Query + Zustand + SSE (EventSource) + Tailwind CSS       │
└───────────────────────────┬─────────────────────────────────────┘
                            │ REST + SSE
┌───────────────────────────▼─────────────────────────────────────┐
│                       FastAPI Backend                            │
│   JWT Auth  │  SlowAPI Rate Limiting  │  StreamingResponse (SSE) │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│               LangGraph Parallel Agent Pipeline                  │
│                                                                  │
│  START                                                           │
│   ├─► Market Research ─────────────┐                            │
│   └─► Competitor Analysis ─────────┤  ← Phase 1 (parallel)     │
│                                    ▼                            │
│                           Product Manager                        │
│                                    │                            │
│                        ┌───────────┤                            │
│                        ▼           ▼                            │
│              Technical Architect  Marketing  ← Phase 3 (parallel)│
│                        │                                        │
│              ┌─────────┤                                        │
│              ▼         ▼                                        │
│    Database Architect  UI/UX       ← Phase 4 (parallel)        │
│              │                                                  │
│           API Design                                            │
│              │                                                  │
│           Roadmap ◄──── waits for UI/UX + Marketing            │
│              │                                                  │
│         Risk Analysis                                           │
│              │                                                  │
│        Revenue & Cost                                           │
│              ▼                                                  │
│            [END]                                                │
└─────────────────────────────────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
     PostgreSQL           Redis           ChromaDB
    (versioned         (24h cache)     (RAG knowledge
      reports)                            base)
```

### Key Design Decisions

**Parallel execution** — Independent agents run concurrently via LangGraph fan-out/fan-in edges, cutting pipeline time ~60% vs sequential.

**SSE over polling** — The frontend subscribes to a Server-Sent Events stream. Each agent completion is pushed instantly instead of waiting for a 3-second poll cycle.

**Blueprint versioning** — Every re-analysis creates a new version. Old versions are preserved so users can compare how an idea evolved across runs.

**Redis cache-aside** — Completed blueprints are cached with a 24h TTL. Repeat views hit Redis instead of Postgres. Graceful fallback if Redis is unavailable.

**RAG context** — Lean startup methodologies and product frameworks are embedded in ChromaDB and retrieved per query to ground agent outputs in real knowledge.

---

## Tech Stack

**Frontend**
- Next.js 15 + TypeScript
- Tailwind CSS (zero UI library — fully custom)
- TanStack Query v5 (server state) + Zustand (client state)
- EventSource API for SSE real-time streaming

**Backend**
- FastAPI + Python 3.11
- LangGraph 0.2 (parallel agent DAG orchestration)
- Google Gemini 2.5 Flash (primary LLM) + OpenRouter free models (fallback)
- SlowAPI (rate limiting — 5 analyses/day per user, keyed by JWT sub)

**Data**
- PostgreSQL with SQLAlchemy 2.0 async + Alembic migrations
- Redis (optional caching — app works without it)
- ChromaDB (local vector store for RAG)
- Sentence Transformers (local embeddings — no API cost)

**DevOps**
- Docker + docker-compose (one command spins up full stack)
- GitHub Actions (CI: pytest + tsc on every PR; CD: Render + Vercel on merge)

---

## Getting Started

### Option A — Docker (one command)

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/FOUNDEROS.git
cd FOUNDEROS
cp backend/.env.example backend/.env   # fill in your API keys
docker-compose up --build
docker-compose exec backend alembic upgrade head
```

Open **http://localhost:3000**

### Option B — Local development

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # add your Gemini + OpenRouter keys
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend && npm install && npm run dev
```

---

## Environment Variables

`backend/.env`:
```env
SECRET_KEY=any-random-string
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/founderos
SYNC_DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/founderos
GEMINI_API_KEY=your-key-from-aistudio.google.com
OPENROUTER_API_KEY=your-key-from-openrouter.ai
REDIS_URL=redis://localhost:6379/0   # optional
```

`frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

> **100% free.** Gemini free tier + OpenRouter free models + Supabase free Postgres + Render free tier + Vercel free tier.

---

## Running Tests

```bash
cd backend && source venv/bin/activate
pytest tests/ -v
```

Uses in-memory SQLite — no Postgres required. LLM calls are mocked.

---

## API Reference

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | — | Register + JWT |
| `POST` | `/api/v1/auth/login` | — | Login + JWT |
| `POST` | `/api/v1/ideas` | ✅ | Create idea |
| `POST` | `/api/v1/ideas/{id}/analyze` | ✅ | Trigger pipeline (5/day) |
| `GET` | `/api/v1/ideas/{id}/stream` | JWT query param | SSE progress stream |
| `GET` | `/api/v1/ideas/{id}/reports?version=N` | ✅ | Reports by version |
| `GET` | `/api/v1/ideas/{id}/versions` | ✅ | All version numbers |
| `POST` | `/api/v1/ideas/{id}/toggle-public` | ✅ | Share blueprint |
| `GET` | `/api/v1/public/blueprints/{id}` | — | Public blueprint view |
| `GET` | `/api/v1/ideas/{id}/export/pdf` | ✅ | Download PDF |
| `GET` | `/api/v1/ideas/{id}/export/markdown` | ✅ | Download Markdown |

Full Swagger UI: **http://localhost:8000/docs**

---

## Features

- ✅ 11 AI agents in a parallel LangGraph DAG
- ✅ Real-time SSE streaming (no polling)
- ✅ Blueprint versioning + history browser
- ✅ Redis caching (cache-aside, 24h TTL)
- ✅ Rate limiting (5/day per user, JWT-keyed)
- ✅ Shareable public blueprint URLs
- ✅ PDF + Markdown export
- ✅ Agent Trace View (prompt, model, tokens, duration)
- ✅ RAG knowledge base (ChromaDB + Sentence Transformers)
- ✅ JWT authentication + session restore
- ✅ Docker + docker-compose
- ✅ GitHub Actions CI/CD
- ✅ Pytest suite (25+ tests, mocked LLMs)

---

*Built by Shreya Goyal*
