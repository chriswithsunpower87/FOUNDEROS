/**
 * File: src/components/workspace/AgentReportCard.tsx
 * Purpose: Collapsible card showing one agent's status and visual output.
 * Responsibilities:
 *   - Show agent icon, name, status badge, and execution time
 *   - Render agent-specific visual layouts (not generic text dumps):
 *       Market Research → TAM/SAM/SOM funnel + trend bars
 *       Competitor Analysis → competitor cards with strength/weakness dots
 *       Product Manager → feature chips + user story cards
 *       Technical Architect → tech stack badges + architecture banner
 *       Database Architect → entity cards + SQL code block
 *       API Design → HTTP method badges per endpoint
 *       UI/UX → screen cards + color palette swatches
 *       Roadmap → week-by-week visual timeline
 *       Marketing → channel cost cards + ICP persona
 *       Risk Analysis → color-coded risk cards + risk level meter
 */

"use client";

import { useState } from "react";
import {
  ChevronDown, ChevronRight, Loader2,
  CheckCircle, XCircle, Clock,
} from "lucide-react";
import { AGENT_LABELS } from "@/lib/constants";
import { cn } from "@/lib/utils";
import type { Report } from "@/types/report.types";

// ── Markdown cleaner ──────────────────────────────────────────────────────────
/**
 * Purpose: Strip LLM markdown syntax from text before rendering in the UI.
 * LLMs often wrap output in **bold**, *italic*, `code`, etc. which appear
 * as literal characters in plain React text nodes.
 */
function cleanText(text: string): string {
  return text
    .replace(/\*\*(.+?)\*\*/gs, "$1")   // **bold** → bold
    .replace(/\*(.+?)\*/gs,     "$1")   // *italic* → italic
    .replace(/#{1,6}\s+/g,      "")     // ## Heading → Heading
    .replace(/`(.+?)`/gs,       "$1")   // `code` → code
    .replace(/^\s*[-*•]\s/gm,   "• ")   // - item / * item → • item
    .trim();
}

// ── Agent config ───────────────────────────────────────────────────────────────
const AGENT_ICONS: Record<string, string> = {
  MARKET_RESEARCH: "📊", COMPETITOR_ANALYSIS: "🔍",
  PRODUCT_MANAGER: "📋", TECHNICAL_ARCHITECT: "🏗️",
  DATABASE_ARCHITECT: "🗄️", API_DESIGN: "🔌",
  UIUX: "🎨", ROADMAP: "🗺️", MARKETING: "📣", RISK_ANALYSIS: "⚠️",
  REVENUE_COST: "💰",
};

// ── Main card ──────────────────────────────────────────────────────────────────
interface AgentReportCardProps { agentType: string; report: Report | null; }

export function AgentReportCard({ agentType, report }: AgentReportCardProps) {
  const [isOpen, setIsOpen] = useState(false);
  const label  = AGENT_LABELS[agentType] ?? agentType;
  const icon   = AGENT_ICONS[agentType] ?? "🤖";
  const status = report?.status ?? "PENDING";

  const cfg = {
    PENDING:   { icon: <Clock       className="w-4 h-4 text-slate-400" />,             badge: "bg-slate-100 text-slate-500",  text: "Pending"  },
    RUNNING:   { icon: <Loader2     className="w-4 h-4 text-blue-500 animate-spin" />, badge: "bg-blue-100 text-blue-600",    text: "Running…" },
    COMPLETED: { icon: <CheckCircle className="w-4 h-4 text-green-500" />,             badge: "bg-green-100 text-green-700",  text: "Complete" },
    FAILED:    { icon: <XCircle     className="w-4 h-4 text-red-500" />,               badge: "bg-red-100 text-red-600",      text: "Failed"   },
  }[status];

  const isExpandable = status === "COMPLETED" && !!report?.output;

  return (
    <div className={cn(
      "bg-white rounded-xl border transition-all duration-200",
      status === "RUNNING"   && "border-blue-200 shadow-sm shadow-blue-50",
      status === "COMPLETED" && "border-slate-200 hover:shadow-sm hover:border-slate-300",
      status === "FAILED"    && "border-red-200",
      status === "PENDING"   && "border-slate-200 opacity-60",
    )}>
      {/* Header */}
      <button
        onClick={() => isExpandable && setIsOpen(!isOpen)}
        className={cn(
          "w-full flex items-center gap-3 p-4 text-left rounded-xl transition-colors",
          isExpandable ? "cursor-pointer hover:bg-slate-50" : "cursor-default",
        )}
      >
        <span className="text-xl w-8 text-center flex-shrink-0">{icon}</span>
        <span className="flex-shrink-0">{cfg.icon}</span>
        <span className="flex-1 text-sm font-semibold text-slate-800">{label}</span>
        <span className={cn("text-xs font-medium px-2 py-0.5 rounded-full flex-shrink-0", cfg.badge)}>{cfg.text}</span>
        {report?.execution_time_ms && (
          <span className="text-xs text-slate-400 flex-shrink-0">{(report.execution_time_ms / 1000).toFixed(1)}s</span>
        )}
        {isExpandable && (isOpen
          ? <ChevronDown  className="w-4 h-4 text-slate-400 flex-shrink-0" />
          : <ChevronRight className="w-4 h-4 text-slate-400 flex-shrink-0" />)}
      </button>

      {/* Running pulse */}
      {status === "RUNNING" && (
        <div className="px-4 pb-3">
          <div className="h-1 bg-blue-100 rounded-full overflow-hidden">
            <div className="h-full w-3/5 bg-blue-400 rounded-full animate-pulse" />
          </div>
          <p className="text-xs text-blue-500 mt-1">Agent is thinking…</p>
        </div>
      )}

      {/* Error */}
      {status === "FAILED" && report?.error_message && (
        <div className="px-4 pb-4">
          <div className="bg-red-50 border border-red-200 text-red-700 text-xs p-3 rounded-lg leading-relaxed">
            {report.error_message}
          </div>
        </div>
      )}

      {/* Content */}
      {isOpen && report?.output && (
        <div className="border-t border-slate-100 px-4 pt-4 pb-5 space-y-5">
          {report.reasoning_summary && (
            <div className="flex items-start gap-2 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2">
              <span className="text-xs">💬</span>
              <p className="text-xs text-slate-500 italic leading-relaxed">{report.reasoning_summary}</p>
            </div>
          )}
          <AgentOutput agentType={agentType} output={report.output as Record<string, unknown>} />
        </div>
      )}
    </div>
  );
}

// ── Router — pick visual renderer per agent ────────────────────────────────────
function AgentOutput({ agentType, output }: { agentType: string; output: Record<string, unknown> }) {
  switch (agentType) {
    case "MARKET_RESEARCH":     return <MarketResearchViz output={output} />;
    case "COMPETITOR_ANALYSIS": return <CompetitorViz output={output} />;
    case "PRODUCT_MANAGER":     return <PRDViz output={output} />;
    case "TECHNICAL_ARCHITECT": return <TechArchViz output={output} />;
    case "DATABASE_ARCHITECT":  return <DatabaseViz output={output} />;
    case "API_DESIGN":          return <APIViz output={output} />;
    case "UIUX":                return <UIUXViz output={output} />;
    case "ROADMAP":             return <RoadmapViz output={output} />;
    case "MARKETING":           return <MarketingViz output={output} />;
    case "RISK_ANALYSIS":       return <RiskViz output={output} />;
    case "REVENUE_COST":        return <RevenueCostViz output={output} />;
    default:                    return <GenericViz output={output} />;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// 1. MARKET RESEARCH
// ═══════════════════════════════════════════════════════════════════════════════
function MarketResearchViz({ output }: { output: Record<string, unknown> }) {
  const trends      = (output.market_trends      as string[] | undefined) ?? [];
  const segments    = (output.target_segments    as string[] | undefined) ?? [];
  const opportunities = (output.market_opportunities as string[] | undefined) ?? [];

  return (
    <div className="space-y-5">
      {/* Industry overview */}
      {output.industry_overview && (
        <Prose label="Industry Overview" text={output.industry_overview as string} color="blue" />
      )}

      {/* Market Size — TAM/SAM/SOM funnel */}
      {output.market_size && (
        <div>
          <Label text="Market Size (TAM → SAM → SOM)" />
          <div className="space-y-2">
            {["TAM", "SAM", "SOM"].map((tier, i) => {
              const widths = ["w-full", "w-4/5", "w-3/5"];
              const colors = ["bg-blue-500", "bg-blue-400", "bg-blue-300"];
              const bgs    = ["bg-blue-50",  "bg-blue-50/70", "bg-blue-50/40"];
              return (
                <div key={tier} className={cn("rounded-lg p-3", bgs[i])}>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-bold text-blue-700">{tier}</span>
                  </div>
                  <div className="w-full bg-blue-100 rounded-full h-2">
                    <div className={cn("h-2 rounded-full", widths[i], colors[i])} />
                  </div>
                </div>
              );
            })}
          </div>
          <p className="text-xs text-slate-600 bg-slate-50 rounded-lg p-3 mt-2 leading-relaxed">
            {output.market_size as string}
          </p>
        </div>
      )}

      {/* Market Trends */}
      {trends.length > 0 && (
        <div>
          <Label text="Market Trends" />
          <div className="space-y-2">
            {trends.map((t, i) => (
              <div key={i} className="flex items-start gap-3 bg-slate-50 rounded-lg px-3 py-2">
                <span className="text-xs font-bold text-slate-400 mt-0.5 w-4 flex-shrink-0">{i + 1}</span>
                <span className="text-sm text-slate-700 leading-relaxed">{t}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Target Segments */}
      {segments.length > 0 && (
        <div>
          <Label text="Target Segments" />
          <div className="grid grid-cols-1 gap-2">
            {segments.map((s, i) => (
              <div key={i} className="flex gap-2 items-start bg-purple-50 border border-purple-100 rounded-lg p-3">
                <span className="text-purple-500 text-sm flex-shrink-0">👤</span>
                <span className="text-sm text-purple-800 leading-relaxed">{s}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Opportunities */}
      {opportunities.length > 0 && (
        <div>
          <Label text="Market Opportunities" />
          <div className="space-y-2">
            {opportunities.map((o, i) => (
              <div key={i} className="flex gap-2 items-start bg-green-50 border border-green-100 rounded-lg p-3">
                <span className="text-green-500 text-sm flex-shrink-0">✦</span>
                <span className="text-sm text-green-800 leading-relaxed">{o}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Potential Demand */}
      {output.potential_demand && (
        <Prose label="Potential Demand" text={output.potential_demand as string} color="green" />
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 2. COMPETITOR ANALYSIS
// ═══════════════════════════════════════════════════════════════════════════════
function CompetitorViz({ output }: { output: Record<string, unknown> }) {
  const competitors = (output.competitors as Record<string, unknown>[] | undefined) ?? [];
  const gaps        = (output.market_gaps as string[] | undefined) ?? [];
  const diffs       = (output.differentiation_opportunities as string[] | undefined) ?? [];

  const headerColors = [
    "from-blue-500 to-blue-600", "from-purple-500 to-purple-600",
    "from-orange-500 to-orange-600", "from-teal-500 to-teal-600",
    "from-rose-500 to-rose-600",
  ];

  return (
    <div className="space-y-5">
      {/* Competitor cards */}
      {competitors.length > 0 && (
        <div>
          <Label text={`${competitors.length} Competitors Identified`} />
          <div className="space-y-3">
            {competitors.map((c, i) => {
              const strengths  = (c.strengths  as string[] | undefined) ?? [];
              const weaknesses = (c.weaknesses as string[] | undefined) ?? [];
              return (
                <div key={i} className="rounded-xl border border-slate-200 overflow-hidden">
                  {/* Colored header */}
                  <div className={cn("bg-gradient-to-r px-4 py-3 text-white", headerColors[i % headerColors.length])}>
                    <p className="font-bold text-sm">{cleanText(String(c.name ?? `Competitor ${i + 1}`))}</p>
                    {c.description && (
                      <p className="text-xs text-white/80 mt-0.5 leading-relaxed">{cleanText(String(c.description))}</p>
                    )}
                  </div>
                  {/* Strengths + Weaknesses */}
                  <div className="grid grid-cols-2 divide-x divide-slate-100 bg-white">
                    <div className="p-3">
                      <p className="text-xs font-semibold text-green-600 mb-2">✅ Strengths</p>
                      <ul className="space-y-1">
                        {strengths.slice(0, 4).map((s, j) => (
                          <li key={j} className="text-xs text-slate-600 flex gap-1.5 leading-relaxed">
                            <span className="text-green-400 flex-shrink-0">•</span>{cleanText(s)}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div className="p-3">
                      <p className="text-xs font-semibold text-red-500 mb-2">❌ Weaknesses</p>
                      <ul className="space-y-1">
                        {weaknesses.slice(0, 4).map((w, j) => (
                          <li key={j} className="text-xs text-slate-600 flex gap-1.5 leading-relaxed">
                            <span className="text-red-400 flex-shrink-0">•</span>{cleanText(w)}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Market Gaps */}
      {gaps.length > 0 && (
        <div>
          <Label text="Market Gaps 🎯" />
          <div className="space-y-2">
            {gaps.map((g, i) => (
              <div key={i} className="bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 text-sm text-amber-800 leading-relaxed">
                {g}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Differentiation */}
      {diffs.length > 0 && (
        <div>
          <Label text="Your Differentiation Opportunities ⭐" />
          <div className="space-y-2">
            {diffs.map((d, i) => (
              <div key={i} className="bg-blue-50 border border-blue-200 rounded-lg px-3 py-2 text-sm text-blue-800 leading-relaxed">
                {d}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 3. PRODUCT MANAGER (PRD)
// ═══════════════════════════════════════════════════════════════════════════════
function PRDViz({ output }: { output: Record<string, unknown> }) {
  const features    = (output.core_features as string[] | undefined) ?? [];
  const userStories = (output.user_stories  as Record<string, unknown>[] | undefined) ?? [];

  return (
    <div className="space-y-5">
      {/* Vision banner */}
      {output.product_vision && (
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl p-4 text-white">
          <p className="text-xs font-semibold text-blue-200 mb-1 uppercase tracking-wide">Product Vision</p>
          <p className="text-sm font-medium leading-relaxed">{String(output.product_vision)}</p>
        </div>
      )}

      {/* Core Features */}
      {features.length > 0 && (
        <div>
          <Label text="Core Features" />
          <div className="grid grid-cols-1 gap-2">
            {features.map((f, i) => (
              <div key={i} className="flex items-center gap-3 bg-slate-50 rounded-lg px-3 py-2.5">
                <span className="w-5 h-5 bg-blue-100 text-blue-600 rounded-full text-xs font-bold flex items-center justify-center flex-shrink-0">{i + 1}</span>
                <span className="text-sm text-slate-700">{f}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* User Stories */}
      {userStories.length > 0 && (
        <div>
          <Label text="User Stories" />
          <div className="space-y-3">
            {userStories.map((s, i) => {
              const criteria = (s.acceptance_criteria as string[] | undefined) ?? [];
              return (
                <div key={i} className="border border-slate-200 rounded-xl overflow-hidden">
                  <div className="bg-slate-800 px-3 py-2 flex items-center gap-2">
                    <span className="text-xs font-mono text-slate-400">US-{String(i + 1).padStart(2, "0")}</span>
                    <span className="text-xs text-slate-200 font-medium">
                      {s.role ?? `As a ${s.as_a ?? "user"}`}
                    </span>
                  </div>
                  <div className="p-3 space-y-2 bg-white">
                    {(s.action ?? s.i_want) && (
                      <p className="text-xs text-slate-700 leading-relaxed">
                        {cleanText(String(s.action ?? s.i_want))}
                      </p>
                    )}
                    {(s.benefit ?? s.so_that) && (
                      <div>
                        <span className="text-xs font-semibold text-slate-500">So that: </span>
                        <span className="text-xs text-slate-600 leading-relaxed">
                          {cleanText(String(s.benefit ?? s.so_that))}
                        </span>
                      </div>
                    )}
                    {criteria.length > 0 && (
                      <div>
                        <p className="text-xs font-semibold text-slate-500 mb-1">Acceptance Criteria</p>
                        <div className="flex flex-wrap gap-1.5">
                          {criteria.map((c, j) => (
                            <span key={j} className="bg-green-50 border border-green-200 text-green-700 text-xs px-2 py-0.5 rounded-full leading-relaxed">
                              ✓ {c}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* PRD Summary */}
      {output.prd_summary && (
        <Prose label="PRD Summary" text={output.prd_summary as string} color="slate" />
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 4. TECHNICAL ARCHITECT
// ═══════════════════════════════════════════════════════════════════════════════
const STACK_COLORS: Record<string, string> = {
  frontend:       "bg-cyan-50 border-cyan-200 text-cyan-800",
  backend:        "bg-green-50 border-green-200 text-green-800",
  database:       "bg-orange-50 border-orange-200 text-orange-800",
  infrastructure: "bg-purple-50 border-purple-200 text-purple-800",
};
const STACK_ICONS: Record<string, string> = {
  frontend: "🖥️", backend: "⚙️", database: "🗄️", infrastructure: "☁️",
};

function TechArchViz({ output }: { output: Record<string, unknown> }) {
  const stack        = (output.recommended_stack as Record<string, unknown> | undefined) ?? {};
  const scalability  = (output.scalability_notes as string[] | undefined) ?? [];

  return (
    <div className="space-y-5">
      {/* Architecture type badge */}
      {output.architecture_type && (
        <div className="bg-gradient-to-r from-slate-700 to-slate-800 text-white rounded-xl p-4">
          <p className="text-xs text-slate-400 font-semibold uppercase tracking-wide mb-1">Architecture Pattern</p>
          <p className="text-sm font-semibold leading-relaxed">{String(output.architecture_type)}</p>
        </div>
      )}

      {/* High Level Design */}
      {output.high_level_design && (
        <Prose label="System Design" text={output.high_level_design as string} color="blue" />
      )}

      {/* Tech Stack */}
      {Object.keys(stack).length > 0 && (
        <div>
          <Label text="Recommended Tech Stack" />
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(stack).map(([layer, tech]) => (
              <div key={layer} className={cn("border rounded-xl p-3", STACK_COLORS[layer] ?? "bg-slate-50 border-slate-200 text-slate-700")}>
                <div className="flex items-center gap-1.5 mb-1">
                  <span className="text-base">{STACK_ICONS[layer] ?? "🔧"}</span>
                  <span className="text-xs font-bold uppercase tracking-wide opacity-70 capitalize">{layer}</span>
                </div>
                <p className="text-xs leading-relaxed">{String(tech)}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Scalability Notes */}
      {scalability.length > 0 && (
        <div>
          <Label text="Scalability Notes" />
          <div className="space-y-2">
            {scalability.map((n, i) => (
              <div key={i} className="flex gap-2 bg-slate-50 rounded-lg px-3 py-2 text-xs text-slate-700 leading-relaxed">
                <span className="text-blue-400 flex-shrink-0">↗</span>{n}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Monolith vs Microservices */}
      {output.microservices_vs_monolith && (
        <Prose label="Architecture Decision" text={output.microservices_vs_monolith as string} color="slate" />
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 5. DATABASE ARCHITECT
// ═══════════════════════════════════════════════════════════════════════════════
function DatabaseViz({ output }: { output: Record<string, unknown> }) {
  const entities      = (output.entities      as Record<string, unknown>[] | undefined) ?? [];
  const relationships = (output.relationships as string[] | undefined) ?? [];

  return (
    <div className="space-y-5">
      {/* Entity cards */}
      {entities.length > 0 && (
        <div>
          <Label text={`${entities.length} Database Tables`} />
          <div className="grid grid-cols-2 gap-2">
            {entities.map((e, i) => {
              const cols = (e.columns as string[] | undefined) ?? [];
              return (
                <div key={i} className="border border-slate-200 rounded-xl overflow-hidden">
                  <div className="bg-slate-800 text-white px-3 py-2">
                    <p className="text-xs font-mono font-bold">{String(e.name ?? `entity_${i}`)}</p>
                    <p className="text-xs text-slate-400">{cols.length} columns</p>
                  </div>
                  <div className="p-2 space-y-0.5">
                    {cols.slice(0, 5).map((col, j) => (
                      <p key={j} className="text-xs font-mono text-slate-600 truncate">{col}</p>
                    ))}
                    {cols.length > 5 && (
                      <p className="text-xs text-slate-400">+{cols.length - 5} more</p>
                    )}
                  </div>
                  {e.description && (
                    <div className="border-t border-slate-100 px-2 py-1.5">
                      <p className="text-xs text-slate-500 leading-relaxed">{String(e.description)}</p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Relationships */}
      {relationships.length > 0 && (
        <div>
          <Label text="Relationships" />
          <div className="space-y-1.5">
            {relationships.map((r, i) => (
              <div key={i} className="flex items-center gap-2 text-xs text-slate-600 bg-slate-50 rounded-lg px-3 py-2">
                <span className="text-blue-400 font-mono">→</span> {r}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SQL Schema */}
      {output.sql_schema && (
        <div>
          <Label text="SQL Schema" />
          <pre className="bg-slate-900 text-green-400 text-xs rounded-xl p-4 overflow-x-auto leading-relaxed whitespace-pre-wrap max-h-64">
            {String(output.sql_schema)}
          </pre>
        </div>
      )}

      {/* Design Notes */}
      {output.design_notes && (
        <Prose label="Design Decisions" text={output.design_notes as string} color="slate" />
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 6. API DESIGN
// ═══════════════════════════════════════════════════════════════════════════════
const METHOD_STYLES: Record<string, string> = {
  GET:    "bg-green-100  text-green-700  border-green-200",
  POST:   "bg-blue-100   text-blue-700   border-blue-200",
  PUT:    "bg-orange-100 text-orange-700 border-orange-200",
  PATCH:  "bg-yellow-100 text-yellow-700 border-yellow-200",
  DELETE: "bg-red-100    text-red-700    border-red-200",
};

function APIViz({ output }: { output: Record<string, unknown> }) {
  const endpoints = (output.endpoints as Record<string, unknown>[] | undefined) ?? [];

  return (
    <div className="space-y-5">
      {endpoints.length > 0 && (
        <div>
          <Label text={`${endpoints.length} API Endpoints`} />
          <div className="space-y-2">
            {endpoints.map((ep, i) => {
              const method = String(ep.method ?? "GET").toUpperCase();
              const methodStyle = METHOD_STYLES[method] ?? "bg-slate-100 text-slate-700 border-slate-200";
              return (
                <div key={i} className="border border-slate-200 rounded-xl overflow-hidden">
                  <div className="flex items-center gap-3 px-3 py-2.5 bg-slate-50">
                    <span className={cn("text-xs font-bold px-2 py-0.5 rounded border font-mono flex-shrink-0", methodStyle)}>
                      {method}
                    </span>
                    <span className="text-xs font-mono text-slate-700 font-semibold truncate flex-1">
                      {String(ep.path ?? "")}
                    </span>
                  </div>
                  {ep.description && (
                    <div className="px-3 py-2 bg-white">
                      <p className="text-xs text-slate-600 leading-relaxed">{String(ep.description)}</p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
      {output.design_notes && (
        <Prose label="Design Principles" text={output.design_notes as string} color="slate" />
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 7. UI/UX
// ═══════════════════════════════════════════════════════════════════════════════
function UIUXViz({ output }: { output: Record<string, unknown> }) {
  const screens    = (output.screens    as Record<string, unknown>[] | undefined) ?? [];
  const principles = (output.design_principles as string[] | undefined) ?? [];

  // Extract hex color codes from the color_scheme string
  const colorText = String(output.color_scheme ?? "");
  const hexColors = colorText.match(/#[0-9A-Fa-f]{6}/g) ?? [];

  return (
    <div className="space-y-5">
      {/* Screens */}
      {screens.length > 0 && (
        <div>
          <Label text={`${screens.length} Screens`} />
          <div className="grid grid-cols-2 gap-2">
            {screens.map((s, i) => {
              const components = (s.components as string[] | undefined) ?? [];
              return (
                <div key={i} className="border border-slate-200 rounded-xl overflow-hidden">
                  {/* Screen "frame" */}
                  <div className="bg-gradient-to-b from-slate-100 to-slate-50 p-3 flex flex-col items-center gap-1 min-h-[80px]">
                    <div className="w-full bg-white rounded border border-slate-200 h-2" />
                    <div className="w-3/4 bg-slate-200 rounded h-1.5" />
                    <div className="w-full bg-slate-100 rounded h-6 mt-1" />
                    <div className="w-full bg-slate-100 rounded h-3" />
                  </div>
                  <div className="p-3 bg-white">
                    <p className="text-xs font-bold text-slate-800 mb-1">{String(s.name ?? `Screen ${i + 1}`)}</p>
                    {s.description && (
                      <p className="text-xs text-slate-500 leading-relaxed mb-2 line-clamp-2">{String(s.description)}</p>
                    )}
                    {components.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {components.slice(0, 3).map((c, j) => (
                          <span key={j} className="bg-slate-100 text-slate-600 text-xs px-1.5 py-0.5 rounded">
                            {c}
                          </span>
                        ))}
                        {components.length > 3 && (
                          <span className="text-xs text-slate-400">+{components.length - 3}</span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Color Palette */}
      {(hexColors.length > 0 || output.color_scheme) && (
        <div>
          <Label text="Color Palette" />
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-3">
            {hexColors.length > 0 && (
              <div className="flex gap-2 mb-3">
                {hexColors.map((hex, i) => (
                  <div key={i} className="flex flex-col items-center gap-1">
                    <div
                      className="w-10 h-10 rounded-lg border border-slate-200 shadow-sm"
                      style={{ backgroundColor: hex }}
                    />
                    <span className="text-xs font-mono text-slate-500">{hex}</span>
                  </div>
                ))}
              </div>
            )}
            <p className="text-xs text-slate-600 leading-relaxed">{colorText}</p>
          </div>
        </div>
      )}

      {/* Typography */}
      {output.typography && (
        <div>
          <Label text="Typography" />
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-3">
            <p className="text-2xl font-bold text-slate-800 mb-1">Aa</p>
            <p className="text-xs text-slate-600 leading-relaxed">{String(output.typography)}</p>
          </div>
        </div>
      )}

      {/* Design Principles */}
      {principles.length > 0 && (
        <div>
          <Label text="Design Principles" />
          <div className="grid grid-cols-2 gap-2">
            {principles.map((p, i) => (
              <div key={i} className="bg-indigo-50 border border-indigo-100 rounded-lg p-3 text-xs text-indigo-800 leading-relaxed">
                {p}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 8. ROADMAP
// ═══════════════════════════════════════════════════════════════════════════════
function RoadmapViz({ output }: { output: Record<string, unknown> }) {
  const weeks = (output.weeks as Record<string, unknown>[] | undefined) ?? [];

  return (
    <div className="space-y-5">
      {/* Duration badge */}
      {output.mvp_duration_weeks && (
        <div className="flex items-center gap-3">
          <div className="bg-blue-600 text-white rounded-xl px-4 py-2 text-sm font-bold">
            {String(output.mvp_duration_weeks)} Week MVP
          </div>
          <span className="text-xs text-slate-500">Week-by-week execution plan</span>
        </div>
      )}

      {/* Timeline */}
      {weeks.length > 0 && (
        <div className="space-y-3">
          {weeks.map((w, i) => {
            const deliverables = (w.deliverables as string[] | undefined) ?? [];
            const isLast = i === weeks.length - 1;
            return (
              <div key={i} className="flex gap-3">
                {/* Timeline connector */}
                <div className="flex flex-col items-center flex-shrink-0">
                  <div className="w-8 h-8 rounded-full bg-blue-600 text-white text-xs font-bold flex items-center justify-center">
                    {String(w.week ?? i + 1)}
                  </div>
                  {!isLast && <div className="w-0.5 bg-blue-200 flex-1 mt-1" />}
                </div>
                {/* Content */}
                <div className="flex-1 pb-3">
                  <div className="bg-white border border-slate-200 rounded-xl p-3">
                    <p className="text-sm font-semibold text-slate-800 mb-1">{String(w.focus ?? "")}</p>
                    {w.milestone && (
                      <div className="flex items-center gap-1.5 mb-2">
                        <span className="text-xs">🏁</span>
                        <span className="text-xs text-green-700 font-medium">{String(w.milestone)}</span>
                      </div>
                    )}
                    {deliverables.length > 0 && (
                      <div className="space-y-1">
                        {deliverables.map((d, j) => (
                          <div key={j} className="flex gap-1.5 text-xs text-slate-600">
                            <span className="text-slate-300 flex-shrink-0">▸</span>{d}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Definition of Done */}
      {output.definition_of_done && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-4">
          <p className="text-xs font-bold text-green-700 mb-1">✅ Definition of Done</p>
          <p className="text-sm text-green-800 leading-relaxed">{String(output.definition_of_done)}</p>
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 9. MARKETING
// ═══════════════════════════════════════════════════════════════════════════════
const COST_STYLE: Record<string, string> = {
  "free":   "bg-green-100 text-green-700 border-green-200",
  "low":    "bg-blue-100  text-blue-700  border-blue-200",
  "medium": "bg-orange-100 text-orange-700 border-orange-200",
};

function MarketingViz({ output }: { output: Record<string, unknown> }) {
  const channels = (output.marketing_channels as Record<string, unknown>[] | undefined) ?? [];
  const tactics  = (output.growth_tactics     as string[] | undefined) ?? [];

  return (
    <div className="space-y-5">
      {/* ICP Persona — handle both string and object from LLM */}
      {output.ideal_customer_profile && (
        <div className="bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-xl p-4">
          <p className="text-xs font-semibold text-violet-200 mb-1 uppercase tracking-wide">Ideal Customer Profile</p>
          {typeof output.ideal_customer_profile === "string" ? (
            <p className="text-sm leading-relaxed">{output.ideal_customer_profile}</p>
          ) : (
            <div className="space-y-1">
              {Object.entries(output.ideal_customer_profile as Record<string, unknown>).map(([k, v]) => (
                <p key={k} className="text-xs text-violet-100 leading-relaxed">
                  <span className="font-semibold capitalize">{k.replace(/_/g, " ")}: </span>
                  {String(v)}
                </p>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Marketing Channels */}
      {channels.length > 0 && (
        <div>
          <Label text="Marketing Channels" />
          <div className="space-y-2">
            {channels.map((ch, i) => {
              const costText  = String(ch.estimated_cost ?? ch.cost ?? "Free");
              const costKey   = costText.toLowerCase().includes("free") ? "free"
                              : costText.toLowerCase().includes("low")  ? "low"
                              : "medium";
              return (
                <div key={i} className="border border-slate-200 rounded-xl p-3 bg-white">
                  <div className="flex items-center justify-between mb-1.5">
                    <p className="text-sm font-semibold text-slate-800">{String(ch.channel ?? `Channel ${i + 1}`)}</p>
                    <span className={cn("text-xs font-medium px-2 py-0.5 rounded-full border", COST_STYLE[costKey])}>
                      {costText}
                    </span>
                  </div>
                  {ch.rationale && (
                    <p className="text-xs text-slate-600 leading-relaxed">{String(ch.rationale)}</p>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Launch Strategy */}
      {output.launch_strategy && (
        <Prose label="Launch Strategy 🚀" text={output.launch_strategy as string} color="blue" />
      )}

      {/* Growth Tactics */}
      {tactics.length > 0 && (
        <div>
          <Label text="Growth Tactics" />
          <div className="space-y-2">
            {tactics.map((t, i) => (
              <div key={i} className="flex gap-3 bg-purple-50 border border-purple-100 rounded-lg px-3 py-2">
                <span className="text-purple-400 font-bold text-xs flex-shrink-0 mt-0.5">{i + 1}</span>
                <span className="text-xs text-purple-800 leading-relaxed">{t}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 10. RISK ANALYSIS
// ═══════════════════════════════════════════════════════════════════════════════
const SEVERITY_STYLE: Record<string, { card: string; badge: string; icon: string }> = {
  HIGH:   { card: "border-red-200 bg-red-50",    badge: "bg-red-100 text-red-700 border-red-200",    icon: "🔴" },
  MEDIUM: { card: "border-yellow-200 bg-yellow-50", badge: "bg-yellow-100 text-yellow-700 border-yellow-200", icon: "🟡" },
  LOW:    { card: "border-green-200 bg-green-50", badge: "bg-green-100 text-green-700 border-green-200", icon: "🟢" },
};

const OVERALL_STYLE: Record<string, string> = {
  HIGH:   "bg-red-600",
  MEDIUM: "bg-yellow-500",
  LOW:    "bg-green-600",
};

function RiskViz({ output }: { output: Record<string, unknown> }) {
  const risks       = (output.risks            as Record<string, unknown>[] | undefined) ?? [];
  const assumptions = (output.key_assumptions  as string[] | undefined) ?? [];
  const failures    = (output.failure_points   as string[] | undefined) ?? [];
  const overallRaw  = String(output.overall_risk_level ?? "");
  const overall     = overallRaw.toUpperCase().startsWith("HIGH")   ? "HIGH"
                    : overallRaw.toUpperCase().startsWith("MEDIUM") ? "MEDIUM"
                    : overallRaw.toUpperCase().startsWith("LOW")    ? "LOW"
                    : null;

  const highCount   = risks.filter(r => String(r.severity).toUpperCase() === "HIGH").length;
  const mediumCount = risks.filter(r => String(r.severity).toUpperCase() === "MEDIUM").length;
  const lowCount    = risks.filter(r => String(r.severity).toUpperCase() === "LOW").length;

  return (
    <div className="space-y-5">
      {/* Overall Risk Meter */}
      {overall && (
        <div className={cn("rounded-xl p-4 text-white", OVERALL_STYLE[overall])}>
          <p className="text-xs font-semibold uppercase tracking-wide text-white/70 mb-1">Overall Risk Level</p>
          <div className="flex items-center gap-3">
            <p className="text-2xl font-black">{overall}</p>
            <div className="flex gap-2 ml-auto text-xs">
              <span className="bg-white/20 rounded px-2 py-0.5">🔴 {highCount} High</span>
              <span className="bg-white/20 rounded px-2 py-0.5">🟡 {mediumCount} Med</span>
              <span className="bg-white/20 rounded px-2 py-0.5">🟢 {lowCount} Low</span>
            </div>
          </div>
        </div>
      )}

      {/* Risk Cards */}
      {risks.length > 0 && (
        <div>
          <Label text={`${risks.length} Identified Risks`} />
          <div className="space-y-2">
            {risks.map((r, i) => {
              const severity = String(r.severity ?? "MEDIUM").toUpperCase() as keyof typeof SEVERITY_STYLE;
              const s = SEVERITY_STYLE[severity] ?? SEVERITY_STYLE.MEDIUM;
              return (
                <div key={i} className={cn("border rounded-xl p-3", s.card)}>
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <p className="text-sm font-semibold text-slate-800">{s.icon} {cleanText(String(r.title ?? `Risk ${i + 1}`))}</p>
                    <span className={cn("text-xs font-bold px-2 py-0.5 rounded-full border flex-shrink-0", s.badge)}>
                      {severity}
                    </span>
                  </div>
                  {r.description && (
                    <p className="text-xs text-slate-700 leading-relaxed mb-2">{cleanText(String(r.description))}</p>
                  )}
                  {r.mitigation && (
                    <div className="bg-white/60 rounded-lg px-2 py-1.5">
                      <span className="text-xs font-semibold text-slate-600">Mitigation: </span>
                      <span className="text-xs text-slate-600 leading-relaxed">{cleanText(String(r.mitigation))}</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Key Assumptions */}
      {assumptions.length > 0 && (
        <div>
          <Label text="Key Assumptions" />
          <div className="space-y-1.5">
            {assumptions.map((a, i) => (
              <div key={i} className="flex gap-2 text-xs text-slate-700 bg-slate-50 rounded-lg px-3 py-2">
                <span className="text-slate-400 flex-shrink-0">◇</span>{a}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Failure Points */}
      {failures.length > 0 && (
        <div>
          <Label text="Most Likely Failure Points" />
          <div className="space-y-2">
            {failures.map((f, i) => (
              <div key={i} className="flex gap-2 bg-red-50 border border-red-200 rounded-lg px-3 py-2 text-xs text-red-800">
                <span className="flex-shrink-0">💀</span>{f}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 11. REVENUE & COST
// ═══════════════════════════════════════════════════════════════════════════════
function RevenueCostViz({ output }: { output: Record<string, unknown> }) {
  const revenueModels  = (output.revenue_models  as Record<string, unknown>[] | undefined) ?? [];
  const pricingTiers   = (output.pricing_tiers   as Record<string, unknown>[] | undefined) ?? [];
  const costBreakdown  = (output.cost_breakdown   as Record<string, unknown> | undefined) ?? {};
  const unitEconomics  = (output.unit_economics   as Record<string, unknown> | undefined) ?? {};
  const projection     = (output.revenue_projection as Record<string, unknown> | undefined) ?? {};

  const recommendedModel = revenueModels.find((m) => m.recommended === true) ?? revenueModels[0];

  return (
    <div className="space-y-5">

      {/* Recommended revenue model */}
      {recommendedModel && (
        <div className="bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-xl p-4">
          <p className="text-xs font-semibold text-emerald-200 mb-1 uppercase tracking-wide">
            Recommended Revenue Model
          </p>
          <p className="text-base font-bold mb-1">{String(recommendedModel.model ?? "")}</p>
          {recommendedModel.description && (
            <p className="text-xs text-emerald-100 leading-relaxed">
              {String(recommendedModel.description)}
            </p>
          )}
        </div>
      )}

      {/* All revenue models */}
      {revenueModels.length > 1 && (
        <div>
          <Label text="Revenue Models Considered" />
          <div className="space-y-2">
            {revenueModels.map((m, i) => (
              <div
                key={i}
                className={cn(
                  "border rounded-xl p-3",
                  m.recommended
                    ? "border-emerald-200 bg-emerald-50"
                    : "border-slate-200 bg-white"
                )}
              >
                <div className="flex items-center justify-between mb-1">
                  <p className="text-sm font-semibold text-slate-800">
                    {String(m.model ?? "")}
                  </p>
                  {m.recommended && (
                    <span className="text-xs bg-emerald-100 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded-full font-medium">
                      ✓ Recommended
                    </span>
                  )}
                </div>
                {m.why_suitable && (
                  <p className="text-xs text-slate-600 leading-relaxed">
                    {String(m.why_suitable)}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Pricing tiers */}
      {pricingTiers.length > 0 && (
        <div>
          <Label text="Pricing Tiers" />
          <div className="grid grid-cols-2 gap-2">
            {pricingTiers.map((t, i) => {
              const features = (t.features as string[] | undefined) ?? [];
              const tierColors = [
                "border-slate-200 bg-slate-50",
                "border-blue-200 bg-blue-50",
                "border-purple-200 bg-purple-50",
                "border-amber-200 bg-amber-50",
              ];
              return (
                <div key={i} className={cn("border rounded-xl p-3", tierColors[i % tierColors.length])}>
                  <p className="text-xs font-bold text-slate-700 uppercase tracking-wide">
                    {String(t.tier ?? `Tier ${i + 1}`)}
                  </p>
                  <p className="text-lg font-black text-slate-900 my-1">
                    {String(t.price ?? "")}
                  </p>
                  {t.target_segment && (
                    <p className="text-xs text-slate-500 mb-2 leading-relaxed">
                      {String(t.target_segment)}
                    </p>
                  )}
                  <ul className="space-y-1">
                    {features.slice(0, 4).map((f, j) => (
                      <li key={j} className="text-xs text-slate-600 flex gap-1.5">
                        <span className="text-emerald-500 flex-shrink-0">✓</span>
                        {f}
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Cost breakdown */}
      {Object.keys(costBreakdown).length > 0 && (
        <div>
          <Label text="Cost Breakdown" />
          <div className="border border-slate-200 rounded-xl overflow-hidden">
            {Object.entries(costBreakdown)
              .filter(([k]) => k !== "total_monthly_burn")
              .map(([k, v], i) => (
                <div
                  key={k}
                  className={cn(
                    "flex items-center justify-between px-4 py-2.5 text-sm",
                    i % 2 === 0 ? "bg-white" : "bg-slate-50"
                  )}
                >
                  <span className="text-slate-600 capitalize">
                    {k.replace(/_/g, " ")}
                  </span>
                  <span className="font-semibold text-slate-800">{String(v)}</span>
                </div>
              ))}
            {costBreakdown.total_monthly_burn && (
              <div className="flex items-center justify-between px-4 py-3 bg-slate-800 text-white">
                <span className="text-sm font-semibold">Total Monthly Burn</span>
                <span className="text-base font-black">
                  {String(costBreakdown.total_monthly_burn)}
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Unit economics */}
      {Object.keys(unitEconomics).length > 0 && (
        <div>
          <Label text="Unit Economics" />
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(unitEconomics).map(([k, v]) => (
              <div key={k} className="bg-blue-50 border border-blue-100 rounded-xl p-3 text-center">
                <p className="text-lg font-black text-blue-700">{String(v)}</p>
                <p className="text-xs text-blue-500 mt-0.5 capitalize">
                  {k.replace(/_/g, " ")}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Revenue projection */}
      {Object.keys(projection).length > 0 && (
        <div>
          <Label text="12-Month Revenue Projection" />
          <div className="grid grid-cols-3 gap-2 mb-2">
            {[
              { key: "month_3",  label: "Month 3"  },
              { key: "month_6",  label: "Month 6"  },
              { key: "month_12", label: "Month 12" },
            ].map(({ key, label }) =>
              projection[key] ? (
                <div key={key} className="bg-emerald-50 border border-emerald-200 rounded-xl p-3 text-center">
                  <p className="text-sm font-black text-emerald-700">
                    {String(projection[key])}
                  </p>
                  <p className="text-xs text-emerald-500 mt-0.5">{label} MRR</p>
                </div>
              ) : null
            )}
          </div>
          {projection.assumptions && (
            <p className="text-xs text-slate-500 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 leading-relaxed italic">
              📌 {String(projection.assumptions)}
            </p>
          )}
        </div>
      )}

      {/* Funding needs */}
      {output.funding_needs && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
          <p className="text-xs font-bold text-amber-700 mb-1">💡 Funding Needs</p>
          <p className="text-sm text-amber-800 leading-relaxed">
            {String(output.funding_needs)}
          </p>
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// GENERIC FALLBACK
// ═══════════════════════════════════════════════════════════════════════════════
function GenericViz({ output }: { output: Record<string, unknown> }) {
  return (
    <div className="space-y-4">
      {Object.entries(output).map(([k, v]) => {
        const label = k.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
        if (Array.isArray(v) && v.every(i => typeof i === "string")) {
          return (
            <div key={k}>
              <Label text={label} />
              <div className="flex flex-wrap gap-2">
                {(v as string[]).map((item, i) => (
                  <span key={i} className="bg-blue-50 border border-blue-100 text-blue-700 text-xs px-3 py-1 rounded-full">{item}</span>
                ))}
              </div>
            </div>
          );
        }
        if (typeof v === "string") return <Prose key={k} label={label} text={v} color="slate" />;
        return null;
      })}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// SHARED PRIMITIVES
// ═══════════════════════════════════════════════════════════════════════════════
function Label({ text }: { text: string }) {
  return (
    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">{text}</p>
  );
}

const PROSE_COLORS: Record<string, string> = {
  blue:  "bg-blue-50  border-blue-100  text-blue-900",
  green: "bg-green-50 border-green-100 text-green-900",
  slate: "bg-slate-50 border-slate-200 text-slate-700",
};

function Prose({ label, text, color = "slate" }: { label: string; text: string; color?: string }) {
  return (
    <div>
      <Label text={label} />
      <p className={cn("text-sm leading-relaxed rounded-xl border px-4 py-3", PROSE_COLORS[color] ?? PROSE_COLORS.slate)}>
        {cleanText(text)}
      </p>
    </div>
  );
}
