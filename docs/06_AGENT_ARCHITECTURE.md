# FounderOS — Agent Architecture

**Version:** 1.0  
**Framework:** LangGraph  
**Primary LLM:** Google Gemini 1.5 Flash (free)  
**Fallback LLM:** OpenRouter free models

---

## 1. Architecture Philosophy

Each agent is an isolated specialist. No agent knows about another's implementation.
They communicate only through a **shared typed state object** — the LangGraph state.

This design is:
- **Testable** — each agent can be unit tested independently
- **Replaceable** — swap any agent's LLM or prompt without touching others
- **Observable** — every agent logs to the `agent_runs` table for trace view

---

## 2. LangGraph State Object

All agents read from and write to a single shared state object passed through the graph.

```python
# File: backend/app/agents/state.py
# Purpose: Defines the shared state schema for the LangGraph agent pipeline

from typing import TypedDict, Optional, List
from app.schemas.report import (
    MarketResearchOutput, CompetitorAnalysisOutput,
    ProductManagerOutput, TechnicalArchitectOutput,
    DatabaseArchitectOutput, ApiDesignOutput,
    UIUXOutput, RoadmapOutput, MarketingOutput, RiskAnalysisOutput
)

class PipelineState(TypedDict):
    """
    Shared state passed between all agents in the LangGraph pipeline.
    Each agent reads from relevant prior fields and writes its own output field.
    """

    # Input (set before pipeline starts)
    idea_id: str
    idea_title: str
    problem_statement: str
    target_audience: str
    rag_context: str                        # Retrieved from ChromaDB

    # Agent Outputs (filled as pipeline runs)
    market_research: Optional[MarketResearchOutput]
    competitor_analysis: Optional[CompetitorAnalysisOutput]
    product_manager: Optional[ProductManagerOutput]
    technical_architect: Optional[TechnicalArchitectOutput]
    database_architect: Optional[DatabaseArchitectOutput]
    api_design: Optional[ApiDesignOutput]
    uiux: Optional[UIUXOutput]
    roadmap: Optional[RoadmapOutput]
    marketing: Optional[MarketingOutput]
    risk_analysis: Optional[RiskAnalysisOutput]

    # Error tracking
    errors: List[str]                       # Accumulates errors without stopping pipeline
```

---

## 3. Base Agent Class

All agents extend `BaseAgent` to ensure consistent behavior.

```python
# File: backend/app/agents/base_agent.py
# Purpose: Abstract base class for all FounderOS AI agents
# Responsibilities:
#   - Provide shared LLM client access
#   - Enforce consistent run() interface
#   - Handle LLM call with Gemini primary + OpenRouter fallback
#   - Log every execution to agent_runs table

from abc import ABC, abstractmethod
from typing import Any, Dict
import time

class BaseAgent(ABC):
    """
    Description: Abstract base for all agents in the FounderOS pipeline.
    Responsibilities:
      - Define the contract (run method) all agents must implement
      - Provide shared LLM calling with automatic fallback
      - Record execution trace to database
    """

    def __init__(self, db_session, agent_name: str):
        self.db = db_session
        self.agent_name = agent_name
        self.gemini_client = build_gemini_client()
        self.openrouter_client = build_openrouter_client()

    @abstractmethod
    def build_prompt(self, state: PipelineState) -> str:
        """Build the full LLM prompt from the current pipeline state."""
        pass

    @abstractmethod
    def parse_output(self, raw_response: str) -> Dict[str, Any]:
        """Parse the LLM's raw string response into a structured dict."""
        pass

    def run(self, state: PipelineState) -> PipelineState:
        """
        Purpose: Execute this agent and return updated pipeline state.
        Parameters:
          state: Current pipeline state with all prior agent outputs
        Returns:
          Updated state with this agent's output field populated
        """
        start_time = time.time()
        prompt = self.build_prompt(state)

        try:
            raw_output = self._call_llm_with_fallback(prompt)
            parsed = self.parse_output(raw_output)
            self._save_trace(state, prompt, parsed, status="COMPLETED", start_time=start_time)
            return self._update_state(state, parsed)
        except Exception as e:
            self._save_trace(state, prompt, None, status="FAILED", error=str(e), start_time=start_time)
            state["errors"].append(f"{self.agent_name}: {str(e)}")
            return state

    def _call_llm_with_fallback(self, prompt: str) -> str:
        """Try Gemini first; fall back to OpenRouter on failure or rate limit."""
        try:
            return self.gemini_client.generate(prompt)
        except RateLimitError:
            return self.openrouter_client.generate(prompt)
```

---

## 4. Agent Execution Graph

```
                    ┌─────────────────────────────────────┐
                    │           PIPELINE START             │
                    │   (idea submitted for analysis)      │
                    └─────────────┬───────────────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                                       ▼
  ┌─────────────────────┐              ┌──────────────────────────┐
  │  Market Research    │              │  Competitor Analysis     │
  │  Agent              │              │  Agent                   │
  │  (Agent 1)          │              │  (Agent 2)               │
  └──────────┬──────────┘              └────────────┬─────────────┘
             │                                      │
             └─────────────┬────────────────────────┘
                           ▼
              ┌────────────────────────┐
              │  Product Manager Agent │
              │  (Agent 3)             │
              │  Reads: 1, 2           │
              └────────────┬───────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
┌─────────────────┐ ┌───────────┐ ┌─────────────────┐
│ Technical       │ │  UI/UX    │ │  Marketing      │
│ Architect       │ │  Agent    │ │  Agent          │
│ (Agent 4)       │ │ (Agent 7) │ │  (Agent 9)      │
│ Reads: 3        │ │ Reads: 3  │ │  Reads: 3       │
└────────┬────────┘ └─────┬─────┘ └────────┬────────┘
         │                │                 │
    ┌────┴────┐           │                 │
    ▼         ▼           │                 │
┌────────┐ ┌──────────┐   │                 │
│Database│ │  API     │   │                 │
│Architect│ │ Design  │   │                 │
│(Agent 5)│ │(Agent 6)│   │                 │
│Reads: 4│ │Reads: 4 │   │                 │
└────┬───┘ └────┬─────┘   │                 │
     │          │          │                 │
     └─────┬────┘          │                 │
           ▼               ▼                 │
     ┌─────────────────────────┐             │
     │     Roadmap Agent       │             │
     │     (Agent 8)           │             │
     │     Reads: 3, 4, 5, 6, 7│             │
     └─────────────┬───────────┘             │
                   │                         │
                   └──────────┬──────────────┘
                              ▼
              ┌───────────────────────────┐
              │    Risk Analysis Agent    │
              │    (Agent 10)             │
              │    Reads: all above       │
              └───────────────┬───────────┘
                              ▼
              ┌───────────────────────────┐
              │    PIPELINE COMPLETE      │
              │    Idea status=COMPLETED  │
              └───────────────────────────┘
```

**Parallel execution:** Agents 1 & 2 run in parallel (no dependencies).
After Agent 3 completes, Agents 4, 7, and 9 run in parallel.
After Agent 4, Agents 5 & 6 run in parallel.
Agent 8 waits for 3, 4, 5, 6, 7.
Agent 10 waits for all others.

---

## 5. Individual Agent Specifications

### Agent 1 — Market Research Agent
```
Input from state:
  - idea_title, problem_statement, target_audience, rag_context

System prompt role: "Expert market research analyst with 15 years experience"

Output fields:
  - industry_overview
  - market_size
  - market_trends (list)
  - market_opportunities (list)
  - potential_demand
  - target_segments (list)

RAG context used: startup market sizing, trend analysis frameworks
```

### Agent 2 — Competitor Analysis Agent
```
Input from state:
  - idea_title, problem_statement, target_audience, rag_context

System prompt role: "Competitive intelligence analyst"

Output fields:
  - competitors (list of name + description + strengths + weaknesses)
  - market_gaps (list)
  - differentiation_opportunities (list)

RAG context used: competitive positioning frameworks, SWOT analysis
```

### Agent 3 — Product Manager Agent
```
Input from state:
  - idea_title, problem_statement, target_audience
  - market_research (from Agent 1)
  - competitor_analysis (from Agent 2)
  - rag_context

System prompt role: "Senior Product Manager at a top-tier tech company"

Output fields:
  - product_vision
  - core_features (list)
  - user_stories (list with acceptance criteria)
  - prd_summary

RAG context used: PRD templates, user story frameworks, agile methodology
```

### Agent 4 — Technical Architect Agent
```
Input from state:
  - idea_title, problem_statement
  - product_manager output (features, user stories)
  - rag_context

System prompt role: "Principal Software Architect"

Output fields:
  - architecture_type
  - recommended_stack
  - high_level_design
  - scalability_notes (list)
  - microservices_vs_monolith

RAG context used: system design patterns, scalability principles
```

### Agents 5–10 follow the same pattern with appropriate inputs and outputs.

---

## 6. LLM Prompt Structure

Every agent uses a structured prompt template:

```
SYSTEM:
You are {role_description}.
You must respond ONLY with valid JSON matching this exact schema: {json_schema}
Do not include markdown code blocks. Do not explain. Output raw JSON only.

CONTEXT (from knowledge base):
{rag_context}

PRIOR AGENT OUTPUTS:
{relevant_prior_outputs_as_json}

TASK:
Analyze the following startup idea and produce the required JSON output.

Startup Idea: {idea_title}
Problem Statement: {problem_statement}
Target Audience: {target_audience}

USER:
Generate the {agent_type} analysis for this startup.
```

---

## 7. Output Parsing Strategy

1. Agent receives raw LLM string response
2. Strip any accidental markdown code fences
3. Parse as JSON with `json.loads()`
4. Validate against Pydantic schema
5. If validation fails → retry once with a corrective prompt
6. If second attempt fails → mark agent as FAILED, continue pipeline

```python
def parse_output(self, raw_response: str) -> Dict[str, Any]:
    """
    Purpose: Convert raw LLM text to validated structured data.
    Parameters:
      raw_response: Raw string from LLM
    Returns:
      Validated dict matching the agent's output schema
    Raises:
      ValueError: If JSON cannot be parsed or schema validation fails
    """
    cleaned = raw_response.strip().removeprefix("```json").removesuffix("```").strip()
    data = json.loads(cleaned)
    validated = self.output_schema(**data)  # Pydantic validation
    return validated.model_dump()
```

---

## 8. Orchestrator

```python
# File: backend/app/agents/orchestrator.py
# Purpose: Build and execute the LangGraph agent pipeline

def build_pipeline_graph(db_session) -> CompiledGraph:
    """
    Purpose: Construct the LangGraph StateGraph with all 10 agents as nodes.
    Returns:
      Compiled LangGraph graph ready for execution
    """
    builder = StateGraph(PipelineState)

    # Register all nodes
    builder.add_node("market_research", MarketResearchAgent(db_session).run)
    builder.add_node("competitor_analysis", CompetitorAnalysisAgent(db_session).run)
    # ... all 10 agents ...

    # Define edges (execution order)
    builder.add_edge(START, "market_research")
    builder.add_edge(START, "competitor_analysis")
    builder.add_edge("market_research", "product_manager")
    builder.add_edge("competitor_analysis", "product_manager")
    builder.add_edge("product_manager", "technical_architect")
    builder.add_edge("product_manager", "uiux")
    builder.add_edge("product_manager", "marketing")
    builder.add_edge("technical_architect", "database_architect")
    builder.add_edge("technical_architect", "api_design")
    builder.add_edge("database_architect", "roadmap")
    builder.add_edge("api_design", "roadmap")
    builder.add_edge("uiux", "roadmap")
    builder.add_edge("roadmap", "risk_analysis")
    builder.add_edge("marketing", "risk_analysis")
    builder.add_edge("risk_analysis", END)

    return builder.compile()
```
