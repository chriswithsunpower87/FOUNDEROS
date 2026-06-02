# FounderOS — System Design

**Version:** 1.0  
**Status:** Approved for Architecture Review

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                             │
│                     Next.js 15 Frontend                         │
│           (Vercel Free Tier — vercel.com)                       │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS (REST + SSE for streaming)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                             │
│              (Render Free Tier — render.com)                    │
│                                                                 │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │  Auth Layer │  │  API Router  │  │   Background Workers  │  │
│  │  (JWT)      │  │  /api/v1/    │  │   (Agent Pipeline)    │  │
│  └─────────────┘  └──────────────┘  └──────────┬────────────┘  │
│                                                 │               │
│                    ┌────────────────────────────┤               │
│                    ▼                            ▼               │
│  ┌─────────────────────────┐   ┌───────────────────────────┐   │
│  │   LangGraph Orchestrator│   │   RAG Pipeline            │   │
│  │   (10 Agent Nodes)      │   │   (ChromaDB + Sentence    │   │
│  └─────────────────────────┘   │    Transformers)          │   │
│                                └───────────────────────────┘   │
└───────┬──────────────────────────────┬──────────────────────────┘
        │                              │
        ▼                              ▼
┌───────────────────┐      ┌───────────────────────┐
│  PostgreSQL DB    │      │  Google Gemini API    │
│  (Supabase Free)  │      │  (Free Tier)          │
│                   │      │  + OpenRouter         │
│  - users          │      │    (Fallback)         │
│  - ideas          │      └───────────────────────┘
│  - reports        │
│  - agent_runs     │      ┌───────────────────────┐
└───────────────────┘      │  ChromaDB             │
                           │  (Local / In-process) │
                           │  - startup knowledge  │
                           └───────────────────────┘
```

---

## 2. Component Breakdown

### 2.1 Frontend — Next.js 15

| Layer | Technology | Purpose |
|---|---|---|
| Routing | Next.js App Router | File-based routing with layouts |
| UI Components | ShadCN UI + Tailwind CSS | Consistent, accessible design system |
| Server State | React Query (TanStack Query) | API data fetching, caching, refetching |
| Client State | Zustand | Auth state, UI state, pipeline status |
| HTTP Client | Axios / fetch | REST API calls to FastAPI |
| Type Safety | TypeScript strict mode | End-to-end type safety |

**Key Pages:**
- `/` — Landing page
- `/login` — Login form
- `/register` — Registration form
- `/dashboard` — Authenticated idea list
- `/ideas/[id]` — Idea workspace (reports + trace view)

### 2.2 Backend — FastAPI

| Layer | Technology | Purpose |
|---|---|---|
| Web Framework | FastAPI | Async REST API |
| ORM | SQLAlchemy 2.0 (async) | Database queries |
| Validation | Pydantic v2 | Request/response schemas |
| Auth | python-jose (JWT) + passlib (bcrypt) | Token generation + password hashing |
| Task Queue | FastAPI BackgroundTasks | Async agent pipeline execution |
| AI Orchestration | LangGraph | Multi-agent workflow graph |
| AI Models | Google Generative AI SDK | Gemini 1.5 Flash (free) |
| AI Fallback | OpenRouter API | Free open-source models |
| Embeddings | Sentence Transformers | `all-MiniLM-L6-v2` model (local) |
| Vector Store | ChromaDB | RAG knowledge retrieval |

### 2.3 Database — PostgreSQL (Supabase)

Supabase provides a managed PostgreSQL instance on the free tier with:
- 500MB storage
- Direct connection string (used by SQLAlchemy)
- Row-level security (optional, handled at app layer)

### 2.4 AI Layer

**Primary:** Google Gemini 1.5 Flash
- Free tier: 15 requests/minute, 1M tokens/day
- Used for all 10 agents

**Fallback:** OpenRouter free models
- `mistralai/mistral-7b-instruct:free`
- `meta-llama/llama-3-8b-instruct:free`
- Triggered automatically when Gemini rate limit is hit

**Agent Framework:** LangGraph
- Each agent = a LangGraph node with typed state
- Directed graph controls execution order
- State passed between nodes (earlier agent output feeds later agents)

---

## 3. Data Flow — Idea Submission to Blueprint

```
1. User submits idea (POST /api/v1/ideas/{id}/analyze)
2. FastAPI creates idea record with status=PENDING
3. BackgroundTask spawns LangGraph orchestrator
4. Orchestrator runs agents in order:
     [Market Research] ──┐
     [Competitor Analysis]┘ → [Product Manager] → [Technical Architect]
                                                          │
                        ┌─────────────────────────────────┤
                        ▼           ▼           ▼         ▼
                   [DB Architect] [API Design] [UI/UX] [Roadmap]
                        └─────────────────────────────────┘
                                         │
                              [Marketing] + [Risk Analysis]
                                         │
                                  [Blueprint Compiler]
5. Each agent writes report to PostgreSQL (reports table)
6. Frontend polls GET /api/v1/ideas/{id}/reports every 3s
7. Reports appear in UI as they complete
8. User exports PDF/Markdown
```

---

## 4. Authentication Flow

```
[User submits login form]
        ↓
[POST /api/v1/auth/login]
        ↓
[FastAPI: verify email + bcrypt password]
        ↓
[Generate JWT (HS256, 7-day expiry)]
        ↓
[Return {access_token, token_type}]
        ↓
[Frontend: store token in Zustand + localStorage]
        ↓
[All subsequent requests: Authorization: Bearer <token>]
        ↓
[FastAPI dependency: get_current_user() verifies token]
```

---

## 5. RAG Pipeline Design

```
[Startup Knowledge Documents]
        ↓
[Sentence Transformers: all-MiniLM-L6-v2]
        ↓
[Vector Embeddings → ChromaDB collection]
        ↓
[At agent execution time:]
  [Agent receives user idea text]
        ↓
  [Query ChromaDB: top-k similar chunks]
        ↓
  [Inject retrieved context into agent prompt]
        ↓
  [LLM generates higher-quality output]
```

---

## 6. Deployment Architecture

| Service | Provider | Free Tier Limits |
|---|---|---|
| Frontend | Vercel | 100GB bandwidth/month, unlimited deploys |
| Backend | Render | 750 hours/month, sleeps after 15min idle |
| Database | Supabase | 500MB storage, 2 projects |
| Vector DB | Render (same container) | In-process ChromaDB, persisted to disk |
| File Storage | Supabase Storage | 1GB free |

**Important:** Render free tier sleeps after 15 minutes of inactivity. The frontend should handle
the cold start gracefully (retry logic, loading states).

---

## 7. Security Design

| Concern | Mitigation |
|---|---|
| Password storage | bcrypt with cost factor 12 |
| JWT signing | HS256 with 256-bit secret key |
| Token expiry | 7 days (configurable) |
| User data isolation | All DB queries filtered by `user_id` from JWT |
| CORS | Backend allows only frontend origin |
| Environment secrets | `.env` files, never committed to git |
| SQL injection | SQLAlchemy parameterized queries (ORM) |
| Rate limiting | Gemini free tier limits act as natural throttle |

---

## 8. Error Handling Strategy

| Layer | Strategy |
|---|---|
| Frontend | React Query retry + error boundary components |
| API | FastAPI HTTPException with structured error responses |
| Agent | Try/catch per agent; failed agents write status=FAILED to DB |
| AI Fallback | If Gemini fails → retry with OpenRouter |
| Pipeline | Failed agent does not stop pipeline; other agents continue |
