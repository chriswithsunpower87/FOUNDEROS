/**
 * File: src/lib/constants.ts
 * Purpose: Application-wide constants.
 * Responsibilities:
 *   - API base URL from environment variable
 *   - Agent type to human-readable label mapping
 *   - Status color and icon mappings
 */

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/** Human-readable labels for each agent type */
export const AGENT_LABELS: Record<string, string> = {
  MARKET_RESEARCH: "Market Research",
  COMPETITOR_ANALYSIS: "Competitor Analysis",
  PRODUCT_MANAGER: "Product Requirements",
  TECHNICAL_ARCHITECT: "Technical Architecture",
  DATABASE_ARCHITECT: "Database Design",
  API_DESIGN: "API Design",
  UIUX: "UI/UX Design",
  ROADMAP: "MVP Roadmap",
  MARKETING: "Go-To-Market Strategy",
  RISK_ANALYSIS: "Risk Analysis",
  REVENUE_COST: "Revenue & Cost Model",
};

/** Ordered list of agents for display */
export const AGENT_ORDER = [
  "MARKET_RESEARCH",
  "COMPETITOR_ANALYSIS",
  "PRODUCT_MANAGER",
  "TECHNICAL_ARCHITECT",
  "DATABASE_ARCHITECT",
  "API_DESIGN",
  "UIUX",
  "ROADMAP",
  "MARKETING",
  "RISK_ANALYSIS",
  "REVENUE_COST",
];

/** Status badge color classes (Tailwind) */
export const STATUS_COLORS: Record<string, string> = {
  DRAFT: "bg-gray-100 text-gray-700",
  PENDING: "bg-yellow-100 text-yellow-700",
  PROCESSING: "bg-blue-100 text-blue-700",
  COMPLETED: "bg-green-100 text-green-700",
  FAILED: "bg-red-100 text-red-700",
  RUNNING: "bg-blue-100 text-blue-700",
};

/** Polling interval for reports during pipeline execution (ms) */
export const REPORTS_POLL_INTERVAL_MS = 3000;
