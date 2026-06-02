# FounderOS — Sequence Diagrams

**Version:** 1.0  
**Format:** Mermaid sequence diagram syntax (renders on GitHub, VS Code, Notion)

---

## 1. User Registration Flow

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend (Next.js)
    participant BE as Backend (FastAPI)
    participant DB as PostgreSQL (Supabase)

    User->>FE: Fill registration form (name, email, password)
    FE->>FE: Validate form with Zod schema
    FE->>BE: POST /api/v1/auth/register
    BE->>BE: Validate request body with Pydantic
    BE->>DB: SELECT * FROM users WHERE email = ?
    DB-->>BE: [] (no existing user)
    BE->>BE: Hash password with bcrypt (cost=12)
    BE->>DB: INSERT INTO users (name, email, password_hash)
    DB-->>BE: New user row
    BE->>BE: Generate JWT (HS256, 7-day expiry)
    BE-->>FE: 201 { user, access_token }
    FE->>FE: Store token in Zustand + localStorage
    FE->>User: Redirect to /dashboard
```

---

## 2. User Login Flow

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend (Next.js)
    participant BE as Backend (FastAPI)
    participant DB as PostgreSQL (Supabase)

    User->>FE: Submit login form (email, password)
    FE->>BE: POST /api/v1/auth/login
    BE->>DB: SELECT * FROM users WHERE email = ?
    DB-->>BE: User row with password_hash
    BE->>BE: bcrypt.verify(password, password_hash)
    alt Password valid
        BE->>BE: Generate JWT
        BE-->>FE: 200 { access_token, user }
        FE->>FE: Store token in Zustand
        FE->>User: Redirect to /dashboard
    else Password invalid
        BE-->>FE: 401 { error: "Invalid credentials" }
        FE->>User: Show error message
    end
```

---

## 3. Create Idea Flow

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend (Next.js)
    participant BE as Backend (FastAPI)
    participant DB as PostgreSQL (Supabase)

    User->>FE: Click "New Idea", fill form
    FE->>BE: POST /api/v1/ideas (Authorization: Bearer token)
    BE->>BE: Verify JWT → extract user_id
    BE->>BE: Validate request body (Pydantic)
    BE->>DB: INSERT INTO ideas (user_id, title, problem_statement, target_audience)
    DB-->>BE: New idea row (status=DRAFT)
    BE-->>FE: 201 { idea }
    FE->>User: Show idea on dashboard + "Analyze" button
```

---

## 4. Trigger Analysis Pipeline Flow

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend (Next.js)
    participant BE as Backend (FastAPI)
    participant DB as PostgreSQL (Supabase)
    participant BG as Background Worker
    participant ORC as LangGraph Orchestrator
    participant LLM as Gemini API

    User->>FE: Click "Analyze" on idea
    FE->>BE: POST /api/v1/ideas/{id}/analyze
    BE->>BE: Verify JWT
    BE->>DB: UPDATE ideas SET status='PENDING'
    BE->>DB: INSERT 10 rows into reports (one per agent, status=PENDING)
    BE-->>FE: 202 Accepted { message: "Pipeline started" }

    Note over BE,BG: BackgroundTask runs asynchronously

    BE->>BG: spawn background task
    BG->>BG: Fetch RAG context from ChromaDB
    BG->>ORC: Execute LangGraph pipeline

    ORC->>DB: UPDATE reports SET status='RUNNING' (Agent 1)
    ORC->>LLM: Agent 1 prompt (Market Research)
    LLM-->>ORC: JSON response
    ORC->>DB: UPDATE reports SET status='COMPLETED', output={...} (Agent 1)

    ORC->>DB: UPDATE reports SET status='RUNNING' (Agent 2)
    ORC->>LLM: Agent 2 prompt (Competitor Analysis)
    LLM-->>ORC: JSON response
    ORC->>DB: UPDATE reports SET status='COMPLETED', output={...} (Agent 2)

    Note over ORC,LLM: Agents 3-10 continue sequentially/in parallel...

    ORC->>DB: UPDATE ideas SET status='COMPLETED'

    Note over FE,BE: Frontend polling happens in parallel

    loop Every 3 seconds while status != COMPLETED
        FE->>BE: GET /api/v1/ideas/{id}/reports
        BE->>DB: SELECT * FROM reports WHERE idea_id=?
        DB-->>BE: Reports array (some COMPLETED, some PENDING)
        BE-->>FE: Reports data
        FE->>User: Update UI — show completed agent cards
    end
```

---

## 5. View Agent Trace Flow

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend (Next.js)
    participant BE as Backend (FastAPI)
    participant DB as PostgreSQL (Supabase)

    User->>FE: Click "View Trace" on completed idea
    FE->>BE: GET /api/v1/ideas/{id}/trace
    BE->>BE: Verify JWT
    BE->>DB: SELECT agent_runs WHERE report_id IN (idea's reports)
    DB-->>BE: All agent_runs rows
    BE-->>FE: Trace data array
    FE->>User: Render Agent Trace View
    Note over FE,User: User can see each agent's prompt, output, model used, tokens
```

---

## 6. Export Blueprint Flow

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend (Next.js)
    participant BE as Backend (FastAPI)
    participant DB as PostgreSQL (Supabase)

    User->>FE: Click "Export PDF"
    FE->>BE: GET /api/v1/ideas/{id}/export/pdf
    BE->>BE: Verify JWT
    BE->>DB: SELECT reports WHERE idea_id=? AND status='COMPLETED'
    DB-->>BE: All completed report outputs
    BE->>BE: Compile all outputs into ordered blueprint
    BE->>BE: Render to PDF (reportlab / weasyprint)
    BE-->>FE: Binary PDF stream (Content-Type: application/pdf)
    FE->>User: Browser downloads PDF file
```

---

## 7. RAG Context Retrieval Flow

```mermaid
sequenceDiagram
    participant ORC as Orchestrator
    participant RAG as RAG Pipeline
    participant ST as Sentence Transformers
    participant VDB as ChromaDB

    ORC->>RAG: retrieve_context(idea_title, problem_statement)
    RAG->>ST: embed("{idea_title}: {problem_statement}")
    ST-->>RAG: query_vector (384-dim)
    RAG->>VDB: query(query_vector, n_results=5)
    VDB-->>RAG: Top 5 relevant knowledge chunks
    RAG->>RAG: Concatenate chunks into context string
    RAG-->>ORC: context_string (max 2000 tokens)
    ORC->>ORC: Inject into PipelineState.rag_context
```

---

## 8. LLM Fallback Flow

```mermaid
sequenceDiagram
    participant Agent as Any Agent
    participant Gemini as Gemini 1.5 Flash
    participant OR as OpenRouter (Free Models)

    Agent->>Gemini: Send prompt
    alt Success
        Gemini-->>Agent: JSON response
    else Rate limit (429) or Error
        Agent->>OR: Send same prompt (Mistral-7B / LLaMA-3-8B)
        alt Success
            OR-->>Agent: JSON response
        else Failure
            Agent->>Agent: Mark as FAILED, add to errors list
            Note over Agent: Pipeline continues with other agents
        end
    end
```
