# FounderOS — Development Roadmap

**Version:** 1.0  
**Total Estimated Duration:** 8 weeks  
**Methodology:** Iterative — each week produces working, testable software  
**Solo Developer** — all tasks sized for one person

---

## Pre-Work: Environment Setup (Day 1 — Before Week 1)

Complete these before writing any code:

| Task | Details |
|---|---|
| Create GitHub repo | `founderos` — initialize with README |
| Install Node.js 20+ | `brew install node` |
| Install Python 3.11+ | `brew install python@3.11` |
| Install PostgreSQL | Use Supabase (no local install needed) |
| Get Gemini API key | `aistudio.google.com` → Create API key (free) |
| Get OpenRouter key | `openrouter.ai` → Register → API key (free) |
| Create Supabase project | `supabase.com` → New project → Copy connection string |
| Create Vercel account | `vercel.com` → Connect GitHub |
| Create Render account | `render.com` → Connect GitHub |
| Install VS Code extensions | Pylance, ESLint, Tailwind IntelliSense, Prettier |

---

## Week 1 — Project Scaffolding + Auth Backend

**Goal:** Working register/login API with database connected.

### Day 1–2: Backend Foundation
- [ ] Create `backend/` folder structure (as per FOLDER_STRUCTURE.md)
- [ ] Initialize Python virtual environment: `python -m venv venv`
- [ ] Install dependencies: FastAPI, SQLAlchemy, Pydantic, python-jose, passlib, alembic
- [ ] Create `backend/app/core/config.py` (Pydantic Settings reading from .env)
- [ ] Create `backend/app/core/database.py` (async SQLAlchemy engine)
- [ ] Create `backend/.env` with Supabase connection string

### Day 3–4: Database Models + Migrations
- [ ] Create SQLAlchemy models: User, Idea, Report, AgentRun
- [ ] Set up Alembic (`alembic init alembic`)
- [ ] Write initial migration: `001_initial_schema.py`
- [ ] Apply migration to Supabase: `alembic upgrade head`

### Day 5–7: Auth API
- [ ] Create `backend/app/core/security.py` (bcrypt + JWT functions)
- [ ] Create `backend/app/core/dependencies.py` (`get_current_user` dependency)
- [ ] Create `backend/app/schemas/auth.py` (RegisterRequest, LoginRequest, TokenResponse)
- [ ] Create `backend/app/services/auth_service.py`
- [ ] Create `backend/app/api/v1/auth.py` (register, login, me endpoints)
- [ ] Mount router in `main.py`
- [ ] Test with Postman or httpie

**Week 1 Deliverable:** `POST /auth/register`, `POST /auth/login`, `GET /auth/me` working against Supabase.

---

## Week 2 — Ideas CRUD API + Frontend Scaffolding

**Goal:** Full ideas CRUD API + Next.js project running.

### Day 1–2: Ideas API
- [ ] Create `backend/app/schemas/idea.py`
- [ ] Create `backend/app/services/idea_service.py`
- [ ] Create `backend/app/api/v1/ideas.py` (full CRUD)
- [ ] Write basic tests in `tests/test_ideas.py`

### Day 3–5: Frontend Setup
- [ ] Create Next.js 15 project: `npx create-next-app@latest frontend --typescript --tailwind --app`
- [ ] Install ShadCN UI: `npx shadcn@latest init`
- [ ] Install React Query, Zustand, Axios: `npm install @tanstack/react-query zustand axios`
- [ ] Create `frontend/src/types/` — all TypeScript types
- [ ] Create `frontend/src/services/api.ts` — Axios instance with interceptors
- [ ] Create `frontend/src/store/authStore.ts` — Zustand auth store

### Day 6–7: Auth Frontend
- [ ] Create Login page + LoginForm component
- [ ] Create Register page + RegisterForm component
- [ ] Create `useAuth` hook
- [ ] Create `ProtectedRoute` component (redirect if no token)
- [ ] Test full register → login → redirect flow

**Week 2 Deliverable:** User can register, login, and reach a protected route. Ideas CRUD API fully working.

---

## Week 3 — Dashboard UI + Idea Management

**Goal:** Users can create, list, and delete startup ideas from the UI.

### Day 1–3: Dashboard Layout
- [ ] Create Dashboard layout (`(dashboard)/layout.tsx`) with sidebar + header
- [ ] Create `AppHeader`, `AppSidebar` shared components (ShadCN-based)
- [ ] Create Dashboard page (`/dashboard`)

### Day 4–5: Idea Components
- [ ] Create `IdeaCard` component (title, status badge, delete/view actions)
- [ ] Create `IdeaList` component (grid layout)
- [ ] Create `CreateIdeaModal` component (form with ShadCN Dialog)
- [ ] Create `DeleteIdeaDialog` component (confirmation)
- [ ] Implement `useIdeas` hook (React Query — list, create, delete)

### Day 6–7: Wire Up + Polish
- [ ] Connect all components to API via React Query
- [ ] Add loading skeletons (ShadCN Skeleton)
- [ ] Add empty state (no ideas yet)
- [ ] Add error handling with toast notifications

**Week 3 Deliverable:** Full dashboard — user sees their ideas, can create and delete them.

---

## Week 4 — RAG Pipeline + First Agent

**Goal:** RAG pipeline working. First agent (Market Research) producing real output.

### Day 1–2: RAG Setup
- [ ] Install Sentence Transformers, ChromaDB: `pip install sentence-transformers chromadb`
- [ ] Create `backend/app/rag/embeddings.py`
- [ ] Create `backend/app/rag/vector_store.py` (ChromaDB client setup)
- [ ] Write knowledge documents in `backend/app/knowledge/`
- [ ] Create `backend/app/rag/knowledge_loader.py` (load docs into ChromaDB)
- [ ] Create `backend/app/rag/retriever.py` (query function)
- [ ] Test: `retriever.retrieve("fitness app")` returns relevant chunks

### Day 3–4: LangGraph + Base Agent
- [ ] Install LangGraph, Google Generative AI SDK: `pip install langgraph google-generativeai`
- [ ] Create `backend/app/agents/state.py` (PipelineState TypedDict)
- [ ] Create `backend/app/agents/base_agent.py` (BaseAgent ABC)
- [ ] Build Gemini + OpenRouter LLM client helpers

### Day 5–7: Market Research Agent
- [ ] Create `market_research_agent.py`
- [ ] Write and tune the prompt
- [ ] Test raw output → parse_output → Pydantic validation
- [ ] Wire up: `POST /ideas/{id}/analyze` triggers just this agent
- [ ] Verify report saved to database correctly

**Week 4 Deliverable:** Market Research Agent generates real output for any startup idea submitted.

---

## Week 5 — All 10 Agents + Orchestrator

**Goal:** Complete agent pipeline running end-to-end.

### Day 1–2: Agents 2–5
- [ ] `competitor_analysis_agent.py` + test
- [ ] `product_manager_agent.py` + test
- [ ] `technical_architect_agent.py` + test
- [ ] `database_architect_agent.py` + test

### Day 3–4: Agents 6–10
- [ ] `api_design_agent.py` + test
- [ ] `uiux_agent.py` + test
- [ ] `roadmap_agent.py` + test
- [ ] `marketing_agent.py` + test
- [ ] `risk_analysis_agent.py` + test

### Day 5–7: Orchestrator + Full Pipeline
- [ ] Create `orchestrator.py` — build complete LangGraph graph
- [ ] Wire `POST /ideas/{id}/analyze` to run full orchestrator in background
- [ ] Test full end-to-end: submit "AI Fitness App" → 10 reports generated
- [ ] Tune prompts where outputs are weak

**Week 5 Deliverable:** Submit any idea → full 10-agent pipeline runs → all reports in database.

---

## Week 6 — Idea Workspace UI + Real-Time Progress

**Goal:** Workspace page showing live agent progress as pipeline runs.

### Day 1–2: Workspace Page Layout
- [ ] Create `/ideas/[id]/page.tsx` — Idea workspace
- [ ] Create `IdeaHeader` component (title, problem, audience)
- [ ] Create `PipelineStatus` component (overall progress bar)

### Day 3–5: Agent Report Cards
- [ ] Create `AgentReportCard` component (collapsible, shows status + output)
- [ ] Implement `useIdeaReports` hook with 3-second polling
- [ ] Show status badges: PENDING (gray) → RUNNING (yellow spinner) → COMPLETED (green) → FAILED (red)
- [ ] Render each agent's JSON output in readable format

### Day 6–7: Agent Trace View
- [ ] Create `AgentTraceView` component
- [ ] Implement `useAgentTrace` hook
- [ ] Display: agent name, model used, tokens used, prompt, output, duration
- [ ] Add tab toggle: "Reports" vs "Trace View"

**Week 6 Deliverable:** Full workspace UI — user watches agents complete in real-time.

---

## Week 7 — Export + Polish

**Goal:** PDF/Markdown export working. App ready for deployment.

### Day 1–3: Export Feature
- [ ] Install reportlab or weasyprint: `pip install reportlab`
- [ ] Create `backend/app/services/export_service.py`
- [ ] Implement `generate_markdown(idea, reports)` — ordered blueprint
- [ ] Implement `generate_pdf(idea, reports)` — styled PDF
- [ ] Create `GET /ideas/{id}/export/pdf` and `/export/markdown` endpoints
- [ ] Create `ExportButtons` frontend component

### Day 4–5: Error Handling + Edge Cases
- [ ] Handle Render cold start (frontend retry + loading state)
- [ ] Handle partial pipeline failure (show failed agents without breaking UI)
- [ ] Add rate limit error handling for Gemini
- [ ] Form validation improvements (Zod schemas)

### Day 6–7: Responsive Design + Final Polish
- [ ] Test on mobile screen sizes
- [ ] Fix any layout issues
- [ ] Add page transitions / animations (Tailwind animate)
- [ ] Final code cleanup + docstrings audit

**Week 7 Deliverable:** Export working. App looks good. Ready to deploy.

---

## Week 8 — Deployment + Documentation

**Goal:** Live on the internet. Documented for portfolio/interview.

### Day 1–2: Backend Deployment (Render)
- [ ] Push code to GitHub
- [ ] Create new Render web service → connect repo
- [ ] Set environment variables in Render dashboard
- [ ] Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Test deployed API with Postman

### Day 3–4: Frontend Deployment (Vercel)
- [ ] Connect GitHub repo to Vercel
- [ ] Set `NEXT_PUBLIC_API_URL` in Vercel environment variables
- [ ] Deploy → test full flow on live domain

### Day 5–6: Final Testing
- [ ] End-to-end test: register → create idea → analyze → export
- [ ] Test on multiple devices/browsers
- [ ] Fix any deployment-specific bugs

### Day 7: Documentation
- [ ] Update README with setup instructions
- [ ] Add architecture diagram to README
- [ ] Record a 2-minute demo video (optional but impressive for portfolio)
- [ ] Write a LinkedIn post describing what you built (AI engineering portfolio)

**Week 8 Deliverable:** FounderOS is live. Portfolio-ready. Demo-able in interviews.

---

## Technology Install Commands (Quick Reference)

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy[asyncio] asyncpg alembic pydantic pydantic-settings \
            python-jose[cryptography] passlib[bcrypt] google-generativeai langgraph \
            sentence-transformers chromadb reportlab python-multipart httpx

# Frontend
cd frontend
npx create-next-app@latest . --typescript --tailwind --app --eslint
npx shadcn@latest init
npm install @tanstack/react-query zustand axios zod react-hook-form @hookform/resolvers
```

---

## Definition of Done — Per Feature

A feature is complete when:
1. Backend endpoint returns correct response (tested in Postman)
2. Frontend displays data correctly
3. Error states handled (API down, empty state, validation errors)
4. Code has header comment block (purpose, responsibilities, dependencies)
5. All functions have docstrings (purpose, params, returns)
