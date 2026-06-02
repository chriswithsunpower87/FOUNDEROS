# FounderOS — Folder Structure

**Version:** 1.0

Every folder and file has a single, clear responsibility. No file exceeds ~300 lines.
All files begin with a header comment block documenting purpose, responsibilities, and dependencies.

---

## Root Layout

```
founderos/
├── frontend/                   # Next.js 15 TypeScript application
├── backend/                    # FastAPI Python application
├── docs/                       # Architecture documents (this folder)
├── .gitignore
└── README.md
```

---

## Frontend Structure

```
frontend/
├── public/
│   └── logo.svg
│
├── src/
│   ├── app/                              # Next.js App Router
│   │   ├── (auth)/                       # Route group — unauthenticated pages
│   │   │   ├── login/
│   │   │   │   └── page.tsx              # Login page
│   │   │   ├── register/
│   │   │   │   └── page.tsx              # Registration page
│   │   │   └── layout.tsx                # Auth layout (centered card)
│   │   │
│   │   ├── (dashboard)/                  # Route group — authenticated pages
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx              # Idea list dashboard
│   │   │   ├── ideas/
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx          # Idea workspace (reports + trace)
│   │   │   └── layout.tsx                # Dashboard layout (sidebar + header)
│   │   │
│   │   ├── layout.tsx                    # Root layout (providers, fonts)
│   │   ├── page.tsx                      # Landing page (/)
│   │   └── globals.css                   # Tailwind base styles
│   │
│   ├── components/
│   │   ├── ui/                           # ShadCN auto-generated components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── skeleton.tsx
│   │   │   └── ...
│   │   │
│   │   ├── auth/                         # Auth-specific components
│   │   │   ├── LoginForm.tsx             # Controlled login form
│   │   │   └── RegisterForm.tsx          # Controlled register form
│   │   │
│   │   ├── dashboard/                    # Dashboard-specific components
│   │   │   ├── IdeaCard.tsx              # Single idea card (title, status, actions)
│   │   │   ├── IdeaList.tsx              # Grid/list of IdeaCards
│   │   │   ├── CreateIdeaModal.tsx       # Modal form to create new idea
│   │   │   └── DeleteIdeaDialog.tsx      # Confirmation dialog for delete
│   │   │
│   │   ├── workspace/                    # Idea workspace components
│   │   │   ├── IdeaHeader.tsx            # Title, problem, audience display
│   │   │   ├── PipelineStatus.tsx        # Overall pipeline progress bar
│   │   │   ├── AgentReportCard.tsx       # Single agent report (collapsible)
│   │   │   ├── AgentTraceView.tsx        # Trace view showing agent execution
│   │   │   └── ExportButtons.tsx         # PDF / Markdown export triggers
│   │   │
│   │   └── shared/                       # App-wide shared components
│   │       ├── AppHeader.tsx             # Top navigation bar
│   │       ├── AppSidebar.tsx            # Left navigation sidebar
│   │       ├── LoadingSpinner.tsx        # Generic loading indicator
│   │       ├── ErrorMessage.tsx          # Reusable error display
│   │       └── ProtectedRoute.tsx        # HOC — redirects unauthenticated users
│   │
│   ├── hooks/                            # Custom React hooks
│   │   ├── useAuth.ts                    # Auth state + login/logout actions
│   │   ├── useIdeas.ts                   # CRUD operations for ideas
│   │   ├── useIdeaReports.ts             # Fetch + poll idea reports
│   │   └── useAgentTrace.ts             # Fetch agent trace data
│   │
│   ├── services/                         # API communication layer
│   │   ├── api.ts                        # Axios instance + interceptors
│   │   ├── authService.ts                # login(), register(), logout()
│   │   ├── ideaService.ts                # createIdea(), listIdeas(), deleteIdea()
│   │   ├── reportService.ts              # getReports(), triggerAnalysis()
│   │   └── exportService.ts             # downloadPDF(), downloadMarkdown()
│   │
│   ├── store/                            # Zustand global state
│   │   ├── authStore.ts                  # User, token, isAuthenticated
│   │   └── uiStore.ts                    # Sidebar open, active modal
│   │
│   ├── types/                            # TypeScript type definitions
│   │   ├── auth.types.ts                 # User, AuthResponse, LoginPayload
│   │   ├── idea.types.ts                 # Idea, IdeaStatus, CreateIdeaPayload
│   │   ├── report.types.ts               # Report, AgentType, ReportStatus
│   │   └── api.types.ts                  # APIResponse<T>, APIError
│   │
│   └── lib/                              # Pure utility functions
│       ├── utils.ts                      # cn() and other helpers
│       ├── constants.ts                  # API_BASE_URL, AGENT_LABELS, etc.
│       └── validators.ts                 # Zod schemas for form validation
│
├── .env.local                            # Local environment variables
├── .env.example                          # Template — commit this
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

---

## Backend Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/                           # All routes versioned under /api/v1
│   │       ├── __init__.py
│   │       ├── router.py                 # Aggregates all v1 routers
│   │       ├── auth.py                   # POST /register, /login, /me
│   │       ├── ideas.py                  # CRUD for ideas
│   │       ├── reports.py                # GET reports, trigger pipeline
│   │       └── export.py                 # PDF / Markdown export endpoints
│   │
│   ├── agents/                           # LangGraph agent implementations
│   │   ├── __init__.py
│   │   ├── base_agent.py                 # Abstract base class for all agents
│   │   ├── state.py                      # LangGraph shared state (TypedDict)
│   │   ├── orchestrator.py               # Builds and runs the LangGraph graph
│   │   ├── market_research_agent.py      # Agent 1
│   │   ├── competitor_analysis_agent.py  # Agent 2
│   │   ├── product_manager_agent.py      # Agent 3
│   │   ├── technical_architect_agent.py  # Agent 4
│   │   ├── database_architect_agent.py   # Agent 5
│   │   ├── api_design_agent.py           # Agent 6
│   │   ├── uiux_agent.py                 # Agent 7
│   │   ├── roadmap_agent.py              # Agent 8
│   │   ├── marketing_agent.py            # Agent 9
│   │   └── risk_analysis_agent.py        # Agent 10
│   │
│   ├── core/                             # Application-level config and setup
│   │   ├── __init__.py
│   │   ├── config.py                     # Pydantic Settings (reads .env)
│   │   ├── database.py                   # SQLAlchemy engine + session factory
│   │   ├── security.py                   # JWT creation/verification, bcrypt
│   │   └── dependencies.py               # FastAPI Depends() helpers (get_current_user)
│   │
│   ├── models/                           # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── base.py                       # DeclarativeBase, common timestamp mixin
│   │   ├── user.py                       # User model
│   │   ├── idea.py                       # Idea model
│   │   ├── report.py                     # Report model
│   │   └── agent_run.py                  # AgentRun model (for trace view)
│   │
│   ├── schemas/                          # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── auth.py                       # RegisterRequest, LoginRequest, TokenResponse
│   │   ├── idea.py                       # CreateIdeaRequest, IdeaResponse
│   │   ├── report.py                     # ReportResponse, AgentRunResponse
│   │   └── common.py                     # PaginatedResponse, ErrorResponse
│   │
│   ├── services/                         # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py               # register_user(), authenticate_user()
│   │   ├── idea_service.py               # create_idea(), list_ideas(), delete_idea()
│   │   ├── report_service.py             # save_report(), get_reports()
│   │   └── export_service.py             # generate_pdf(), generate_markdown()
│   │
│   ├── rag/                              # RAG pipeline
│   │   ├── __init__.py
│   │   ├── embeddings.py                 # SentenceTransformer wrapper
│   │   ├── vector_store.py               # ChromaDB client + collection setup
│   │   ├── knowledge_loader.py           # Load startup docs into ChromaDB
│   │   └── retriever.py                  # Query ChromaDB, return context strings
│   │
│   ├── knowledge/                        # Startup methodology documents (plain text)
│   │   ├── lean_startup.txt
│   │   ├── jobs_to_be_done.txt
│   │   ├── product_development.txt
│   │   └── go_to_market.txt
│   │
│   └── main.py                           # FastAPI app factory, middleware, router mount
│
├── alembic/                              # Database migrations
│   ├── versions/
│   │   └── 001_initial_schema.py
│   ├── env.py
│   └── alembic.ini
│
├── tests/
│   ├── test_auth.py
│   ├── test_ideas.py
│   └── test_agents.py
│
├── .env                                  # Local environment variables (never commit)
├── .env.example                          # Template — commit this
├── requirements.txt
└── README.md
```

---

## Naming Conventions

| Type | Convention | Example |
|---|---|---|
| Python files | `snake_case.py` | `market_research_agent.py` |
| Python classes | `PascalCase` | `MarketResearchAgent` |
| Python functions | `snake_case` | `run_market_research()` |
| TypeScript files | `PascalCase.tsx` for components | `IdeaCard.tsx` |
| TypeScript files | `camelCase.ts` for non-components | `ideaService.ts` |
| TypeScript types | `PascalCase` | `IdeaResponse` |
| TypeScript interfaces | `PascalCase` | `CreateIdeaPayload` |
| CSS classes | Tailwind utility classes only | `flex items-center gap-4` |
| Environment vars | `SCREAMING_SNAKE_CASE` | `GEMINI_API_KEY` |
| Database tables | `snake_case` plural | `agent_runs` |
| Database columns | `snake_case` | `created_at` |
