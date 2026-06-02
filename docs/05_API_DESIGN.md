# FounderOS — API Design

**Version:** 1.0  
**Base URL:** `https://founderos-api.onrender.com/api/v1`  
**Auth:** Bearer JWT token in `Authorization` header  
**Format:** JSON request/response bodies

---

## 1. Standard Response Envelopes

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional human-readable message"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "IDEA_NOT_FOUND",
    "message": "Idea with id abc-123 not found",
    "details": {}
  }
}
```

### HTTP Status Codes Used

| Code | Meaning |
|---|---|
| 200 | OK — successful GET, PUT |
| 201 | Created — successful POST |
| 204 | No Content — successful DELETE |
| 400 | Bad Request — validation error |
| 401 | Unauthorized — missing/invalid token |
| 403 | Forbidden — resource belongs to another user |
| 404 | Not Found — resource doesn't exist |
| 422 | Unprocessable Entity — Pydantic validation failure |
| 429 | Too Many Requests — rate limit hit |
| 500 | Internal Server Error |

---

## 2. Auth Endpoints

### POST `/auth/register`
Register a new user account.

**Request Body:**
```json
{
  "name": "Shansit Goyal",
  "email": "shansit@example.com",
  "password": "SecurePass123!"
}
```

**Response 201:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid-here",
      "name": "Shansit Goyal",
      "email": "shansit@example.com",
      "created_at": "2026-06-02T10:00:00Z"
    },
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

---

### POST `/auth/login`
Authenticate and receive a JWT.

**Request Body:**
```json
{
  "email": "shansit@example.com",
  "password": "SecurePass123!"
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": "uuid-here",
      "name": "Shansit Goyal",
      "email": "shansit@example.com"
    }
  }
}
```

---

### GET `/auth/me`
Get current authenticated user's profile.

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "success": true,
  "data": {
    "id": "uuid-here",
    "name": "Shansit Goyal",
    "email": "shansit@example.com",
    "created_at": "2026-06-02T10:00:00Z"
  }
}
```

---

## 3. Ideas Endpoints

### GET `/ideas`
List all ideas belonging to the authenticated user.

**Headers:** `Authorization: Bearer <token>`

**Query Params:**
- `status` (optional): filter by status (`DRAFT`, `COMPLETED`, etc.)
- `page` (optional, default=1)
- `page_size` (optional, default=20)

**Response 200:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "uuid-here",
        "title": "AI Fitness App",
        "problem_statement": "People struggle to stay consistent with workouts",
        "target_audience": "Busy professionals aged 25-40",
        "status": "COMPLETED",
        "created_at": "2026-06-02T10:00:00Z",
        "updated_at": "2026-06-02T10:05:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20
  }
}
```

---

### POST `/ideas`
Create a new startup idea.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "title": "AI Fitness App",
  "problem_statement": "People struggle to stay consistent with workouts without personalized coaching",
  "target_audience": "Busy professionals aged 25-40 who want to get fit but lack time"
}
```

**Response 201:**
```json
{
  "success": true,
  "data": {
    "id": "uuid-here",
    "title": "AI Fitness App",
    "problem_statement": "...",
    "target_audience": "...",
    "status": "DRAFT",
    "created_at": "2026-06-02T10:00:00Z"
  }
}
```

---

### GET `/ideas/{idea_id}`
Get a single idea by ID.

**Headers:** `Authorization: Bearer <token>`

**Response 200:** Same shape as single item in the list above.

**Response 404:** If idea not found or belongs to different user.

---

### PUT `/ideas/{idea_id}`
Update an idea's metadata. Only allowed when status is `DRAFT`.

**Request Body:** (all fields optional)
```json
{
  "title": "AI Fitness Coach App",
  "problem_statement": "Updated problem...",
  "target_audience": "Updated audience..."
}
```

**Response 200:** Updated idea object.

---

### DELETE `/ideas/{idea_id}`
Delete an idea and all associated reports.

**Headers:** `Authorization: Bearer <token>`

**Response 204:** No content.

---

## 4. Analysis Endpoints

### POST `/ideas/{idea_id}/analyze`
Trigger the full 10-agent AI pipeline for an idea.
Sets idea status to `PENDING`, creates 10 `reports` rows, runs pipeline in background.

**Headers:** `Authorization: Bearer <token>`

**Response 202 (Accepted):**
```json
{
  "success": true,
  "data": {
    "message": "Analysis pipeline started",
    "idea_id": "uuid-here",
    "status": "PENDING"
  }
}
```

**Validation:** Returns 400 if idea is already `PROCESSING` or `COMPLETED`.

---

### GET `/ideas/{idea_id}/reports`
Get all agent reports for an idea. Frontend polls this every 3 seconds during processing.

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-here",
      "idea_id": "uuid-here",
      "agent_type": "MARKET_RESEARCH",
      "status": "COMPLETED",
      "output": {
        "industry_overview": "The global fitness technology market...",
        "market_trends": ["AI-personalized coaching", "Wearable integration"],
        "market_opportunities": ["Untapped rural market", "Senior fitness segment"],
        "potential_demand": "High — $14B market growing at 23% CAGR"
      },
      "reasoning_summary": "Analyzed fitness tech market using trend data and industry reports",
      "execution_time_ms": 4200,
      "created_at": "2026-06-02T10:00:00Z",
      "updated_at": "2026-06-02T10:00:04Z"
    },
    {
      "agent_type": "COMPETITOR_ANALYSIS",
      "status": "RUNNING",
      "output": null
    }
  ]
}
```

---

### GET `/ideas/{idea_id}/trace`
Get the full agent trace for the Agent Trace View feature.
Returns every run attempt with input, output, and prompts used.

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-here",
      "report_id": "uuid-here",
      "agent_name": "Market Research Agent",
      "input_snapshot": { "idea_title": "AI Fitness App", "rag_context": "..." },
      "output_snapshot": { "industry_overview": "..." },
      "prompt_used": "You are an expert market research analyst...",
      "model_used": "gemini-1.5-flash",
      "tokens_used": 1840,
      "status": "COMPLETED",
      "started_at": "2026-06-02T10:00:00Z",
      "completed_at": "2026-06-02T10:00:04Z"
    }
  ]
}
```

---

## 5. Export Endpoints

### GET `/ideas/{idea_id}/export/pdf`
Generate and return a PDF of the full startup blueprint.

**Response:** Binary PDF file  
**Headers:** `Content-Type: application/pdf`  
**Content-Disposition:** `attachment; filename="ai-fitness-app-blueprint.pdf"`

---

### GET `/ideas/{idea_id}/export/markdown`
Generate and return a Markdown file of the full blueprint.

**Response:** Plain text Markdown  
**Headers:** `Content-Type: text/markdown`  
**Content-Disposition:** `attachment; filename="ai-fitness-app-blueprint.md"`

---

## 6. Agent Output Schemas (JSONB field shapes)

Each agent writes structured JSON into `reports.output`. Schemas below:

### MARKET_RESEARCH output
```json
{
  "industry_overview": "string",
  "market_size": "string",
  "market_trends": ["string"],
  "market_opportunities": ["string"],
  "potential_demand": "string",
  "target_segments": ["string"]
}
```

### COMPETITOR_ANALYSIS output
```json
{
  "competitors": [
    {
      "name": "string",
      "description": "string",
      "strengths": ["string"],
      "weaknesses": ["string"]
    }
  ],
  "market_gaps": ["string"],
  "differentiation_opportunities": ["string"]
}
```

### PRODUCT_MANAGER output
```json
{
  "product_vision": "string",
  "core_features": ["string"],
  "user_stories": [
    {
      "role": "string",
      "action": "string",
      "benefit": "string",
      "acceptance_criteria": ["string"]
    }
  ],
  "prd_summary": "string"
}
```

### TECHNICAL_ARCHITECT output
```json
{
  "architecture_type": "string",
  "recommended_stack": { "frontend": "...", "backend": "...", "database": "..." },
  "high_level_design": "string",
  "scalability_notes": ["string"],
  "microservices_vs_monolith": "string"
}
```

### DATABASE_ARCHITECT output
```json
{
  "entities": [{ "name": "string", "columns": ["string"], "description": "string" }],
  "relationships": ["string"],
  "sql_schema": "string",
  "design_notes": "string"
}
```

### API_DESIGN output
```json
{
  "endpoints": [
    {
      "method": "POST",
      "path": "/api/v1/users",
      "description": "string",
      "request_example": {},
      "response_example": {}
    }
  ]
}
```

### UIUX output
```json
{
  "screens": [
    {
      "name": "string",
      "description": "string",
      "components": ["string"],
      "user_flow": "string"
    }
  ],
  "design_principles": ["string"]
}
```

### ROADMAP output
```json
{
  "mvp_duration_weeks": 8,
  "weeks": [
    {
      "week": 1,
      "focus": "string",
      "deliverables": ["string"],
      "milestone": "string"
    }
  ]
}
```

### MARKETING output
```json
{
  "ideal_customer_profile": "string",
  "marketing_channels": [{ "channel": "string", "rationale": "string" }],
  "launch_strategy": "string",
  "growth_tactics": ["string"]
}
```

### RISK_ANALYSIS output
```json
{
  "risks": [
    {
      "title": "string",
      "description": "string",
      "severity": "HIGH | MEDIUM | LOW",
      "mitigation": "string"
    }
  ],
  "key_assumptions": ["string"],
  "failure_points": ["string"]
}
```
