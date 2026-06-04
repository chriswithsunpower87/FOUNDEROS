/**
 * File: src/types/report.types.ts
 * Purpose: TypeScript types for agent reports and trace data.
 */

export type AgentType =
  | "MARKET_RESEARCH"
  | "COMPETITOR_ANALYSIS"
  | "PRODUCT_MANAGER"
  | "TECHNICAL_ARCHITECT"
  | "DATABASE_ARCHITECT"
  | "API_DESIGN"
  | "UIUX"
  | "ROADMAP"
  | "MARKETING"
  | "RISK_ANALYSIS"
  | "REVENUE_COST";

export type ReportStatus = "PENDING" | "RUNNING" | "COMPLETED" | "FAILED";

export interface Report {
  id: string;
  idea_id: string;
  agent_type: AgentType;
  status: ReportStatus;
  output: Record<string, unknown> | null;
  reasoning_summary: string | null;
  error_message: string | null;
  execution_time_ms: number | null;
  version: number;    // Which analysis run (1 = first, 2 = first re-run, etc.)
  created_at: string;
  updated_at: string;
}

export interface AgentRun {
  id: string;
  report_id: string;
  agent_name: string;
  input_snapshot: Record<string, unknown>;
  output_snapshot: Record<string, unknown> | null;
  prompt_used: string | null;
  model_used: string | null;
  tokens_used: number | null;
  status: ReportStatus;
  error_message: string | null;
  started_at: string;
  completed_at: string | null;
}
