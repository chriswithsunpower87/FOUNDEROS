/**
 * File: src/components/workspace/AgentReportCard.tsx
 * Purpose: Collapsible card showing one agent's status and output.
 * Responsibilities:
 *   - Show agent icon, name, status badge, and execution time
 *   - Expand to show structured output with visual sections:
 *       pills for short list items, mini-cards for object arrays,
 *       code blocks for SQL/code fields, prose for long text
 *   - Show spinner while RUNNING, error if FAILED
 */

"use client";

import { useState } from "react";
import {
  ChevronDown,
  ChevronRight,
  Loader2,
  CheckCircle,
  XCircle,
  Clock,
} from "lucide-react";
import { AGENT_LABELS } from "@/lib/constants";
import { cn } from "@/lib/utils";
import type { Report } from "@/types/report.types";

// ── Agent icons (emoji) ────────────────────────────────────────────────────────
const AGENT_ICONS: Record<string, string> = {
  MARKET_RESEARCH:     "📊",
  COMPETITOR_ANALYSIS: "🔍",
  PRODUCT_MANAGER:     "📋",
  TECHNICAL_ARCHITECT: "🏗️",
  DATABASE_ARCHITECT:  "🗄️",
  API_DESIGN:          "🔌",
  UIUX:                "🎨",
  ROADMAP:             "🗺️",
  MARKETING:           "📣",
  RISK_ANALYSIS:       "⚠️",
};

// ── Fields that should render as a code block ──────────────────────────────────
const CODE_FIELDS = new Set(["sql_schema", "schema", "sql", "code"]);

// ── Fields that are long prose — render as paragraph, not pill ────────────────
const PROSE_FIELDS = new Set([
  "prd_summary", "high_level_design", "microservices_vs_monolith",
  "design_notes", "design_principles_text", "launch_strategy",
  "ideal_customer_profile", "overall_risk_level", "definition_of_done",
  "architecture_type", "color_scheme", "typography", "market_size",
  "potential_demand", "industry_overview",
]);

interface AgentReportCardProps {
  agentType: string;
  report: Report | null;
}

export function AgentReportCard({ agentType, report }: AgentReportCardProps) {
  const [isOpen, setIsOpen] = useState(false);
  const label  = AGENT_LABELS[agentType] ?? agentType;
  const icon   = AGENT_ICONS[agentType] ?? "🤖";
  const status = report?.status ?? "PENDING";

  const statusConfig = {
    PENDING:   { icon: <Clock      className="w-4 h-4 text-slate-400" />,              badge: "bg-slate-100 text-slate-500",  text: "Pending"   },
    RUNNING:   { icon: <Loader2    className="w-4 h-4 text-blue-500 animate-spin" />,  badge: "bg-blue-100 text-blue-600",    text: "Running…"  },
    COMPLETED: { icon: <CheckCircle className="w-4 h-4 text-green-500" />,             badge: "bg-green-100 text-green-700",  text: "Complete"  },
    FAILED:    { icon: <XCircle    className="w-4 h-4 text-red-500" />,               badge: "bg-red-100 text-red-600",      text: "Failed"    },
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

      {/* ── Header ────────────────────────────────────────────────────────────── */}
      <button
        onClick={() => isExpandable && setIsOpen(!isOpen)}
        className={cn(
          "w-full flex items-center gap-3 p-4 text-left rounded-xl transition-colors",
          isExpandable ? "cursor-pointer hover:bg-slate-50" : "cursor-default",
        )}
      >
        {/* Agent emoji icon */}
        <span className="text-xl w-8 text-center flex-shrink-0" aria-hidden="true">
          {icon}
        </span>

        {/* Status icon */}
        <span className="flex-shrink-0">{statusConfig.icon}</span>

        {/* Label */}
        <span className="flex-1 text-sm font-semibold text-slate-800">{label}</span>

        {/* Status badge */}
        <span className={cn("text-xs font-medium px-2 py-0.5 rounded-full flex-shrink-0", statusConfig.badge)}>
          {statusConfig.text}
        </span>

        {/* Duration */}
        {report?.execution_time_ms && (
          <span className="text-xs text-slate-400 flex-shrink-0">
            {(report.execution_time_ms / 1000).toFixed(1)}s
          </span>
        )}

        {/* Chevron */}
        {isExpandable && (
          isOpen
            ? <ChevronDown  className="w-4 h-4 text-slate-400 flex-shrink-0" />
            : <ChevronRight className="w-4 h-4 text-slate-400 flex-shrink-0" />
        )}
      </button>

      {/* ── Running pulse ─────────────────────────────────────────────────────── */}
      {status === "RUNNING" && (
        <div className="px-4 pb-3">
          <div className="h-1 bg-blue-100 rounded-full overflow-hidden">
            <div className="h-full bg-blue-400 rounded-full animate-pulse" style={{ width: "60%" }} />
          </div>
          <p className="text-xs text-blue-500 mt-1">Agent is thinking…</p>
        </div>
      )}

      {/* ── Error ─────────────────────────────────────────────────────────────── */}
      {status === "FAILED" && report?.error_message && (
        <div className="px-4 pb-4">
          <div className="bg-red-50 border border-red-200 text-red-700 text-xs p-3 rounded-lg leading-relaxed">
            {report.error_message}
          </div>
        </div>
      )}

      {/* ── Expanded output ───────────────────────────────────────────────────── */}
      {isOpen && report?.output && (
        <div className="border-t border-slate-100 px-4 pt-4 pb-5 space-y-5">
          {/* Reasoning chip */}
          {report.reasoning_summary && (
            <div className="flex items-start gap-2 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2">
              <span className="text-xs">💬</span>
              <p className="text-xs text-slate-500 italic leading-relaxed">
                {report.reasoning_summary}
              </p>
            </div>
          )}

          <OutputRenderer output={report.output} />
        </div>
      )}
    </div>
  );
}

// ── Output renderer ────────────────────────────────────────────────────────────

function OutputRenderer({ output }: { output: Record<string, unknown> }) {
  return (
    <div className="space-y-5">
      {Object.entries(output).map(([key, value]) => (
        <OutputSection key={key} fieldKey={key} value={value} />
      ))}
    </div>
  );
}

function OutputSection({ fieldKey, value }: { fieldKey: string; value: unknown }) {
  const label = fieldKey
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());

  // ── Code block ──────────────────────────────────────────────────────────────
  if (CODE_FIELDS.has(fieldKey) && typeof value === "string") {
    return (
      <div>
        <SectionLabel label={label} />
        <pre className="bg-slate-900 text-green-400 text-xs rounded-lg p-4 overflow-x-auto leading-relaxed whitespace-pre-wrap">
          {value}
        </pre>
      </div>
    );
  }

  // ── Array of strings → pills ─────────────────────────────────────────────
  if (Array.isArray(value) && value.every((v) => typeof v === "string")) {
    return (
      <div>
        <SectionLabel label={label} />
        <div className="flex flex-wrap gap-2">
          {(value as string[]).map((item, i) => (
            <span
              key={i}
              className="bg-blue-50 border border-blue-100 text-blue-700 text-xs px-3 py-1 rounded-full leading-relaxed"
            >
              {item}
            </span>
          ))}
        </div>
      </div>
    );
  }

  // ── Array of objects → mini-cards ────────────────────────────────────────
  if (Array.isArray(value) && value.some((v) => typeof v === "object" && v !== null)) {
    return (
      <div>
        <SectionLabel label={label} />
        <div className="space-y-3">
          {(value as Record<string, unknown>[]).map((item, i) => (
            <MiniCard key={i} data={item} index={i} />
          ))}
        </div>
      </div>
    );
  }

  // ── Plain object → key-value rows ─────────────────────────────────────────
  if (typeof value === "object" && value !== null && !Array.isArray(value)) {
    return (
      <div>
        <SectionLabel label={label} />
        <div className="bg-slate-50 border border-slate-200 rounded-lg divide-y divide-slate-100">
          {Object.entries(value as Record<string, unknown>).map(([k, v]) => (
            <div key={k} className="flex gap-3 px-3 py-2">
              <span className="text-xs font-medium text-slate-500 w-24 flex-shrink-0 capitalize">
                {k.replace(/_/g, " ")}
              </span>
              <span className="text-xs text-slate-700 leading-relaxed flex-1">
                {String(v)}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // ── Long prose fields → paragraph ─────────────────────────────────────────
  if (PROSE_FIELDS.has(fieldKey) || (typeof value === "string" && value.length > 120)) {
    return (
      <div>
        <SectionLabel label={label} />
        <p className="text-sm text-slate-700 leading-relaxed bg-slate-50 border border-slate-100 rounded-lg px-4 py-3">
          {String(value)}
        </p>
      </div>
    );
  }

  // ── Short string → inline value ───────────────────────────────────────────
  return (
    <div className="flex items-start gap-3">
      <span className="text-xs font-semibold text-slate-500 w-36 flex-shrink-0 pt-0.5 uppercase tracking-wide">
        {label}
      </span>
      <span className="text-sm text-slate-800 flex-1 leading-relaxed font-medium">
        {String(value)}
      </span>
    </div>
  );
}

// ── Mini-card for object array items (competitors, user stories, risks, etc.) ─

function MiniCard({ data, index }: { data: Record<string, unknown>; index: number }) {
  const entries = Object.entries(data);
  // First entry is usually the "title" or "name"
  const [titleKey, titleValue] = entries[0] ?? [];
  const rest = entries.slice(1);

  return (
    <div className="bg-white border border-slate-200 rounded-lg p-3 space-y-2">
      {/* Title row */}
      {titleValue && (
        <div className="flex items-center gap-2">
          <span className="bg-slate-100 text-slate-500 text-xs font-mono w-5 h-5 rounded flex items-center justify-center flex-shrink-0">
            {index + 1}
          </span>
          <span className="text-sm font-semibold text-slate-800">
            {String(titleValue)}
          </span>
        </div>
      )}

      {/* Rest of fields */}
      {rest.map(([k, v]) => {
        const fieldLabel = k.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

        if (Array.isArray(v)) {
          return (
            <div key={k}>
              <p className="text-xs font-medium text-slate-500 mb-1">{fieldLabel}</p>
              <div className="flex flex-wrap gap-1.5">
                {(v as unknown[]).map((item, i) => (
                  <span
                    key={i}
                    className="bg-slate-100 text-slate-600 text-xs px-2 py-0.5 rounded-full"
                  >
                    {String(item)}
                  </span>
                ))}
              </div>
            </div>
          );
        }

        // Severity badge
        if (k === "severity") {
          const color =
            String(v) === "HIGH"   ? "bg-red-100 text-red-700 border-red-200" :
            String(v) === "MEDIUM" ? "bg-yellow-100 text-yellow-700 border-yellow-200" :
                                     "bg-green-100 text-green-700 border-green-200";
          return (
            <div key={k} className="flex items-center gap-2">
              <span className="text-xs text-slate-500">{fieldLabel}:</span>
              <span className={cn("text-xs font-semibold px-2 py-0.5 rounded-full border", color)}>
                {String(v)}
              </span>
            </div>
          );
        }

        return (
          <div key={k}>
            <p className="text-xs font-medium text-slate-500 mb-0.5">{fieldLabel}</p>
            <p className="text-xs text-slate-700 leading-relaxed">{String(v)}</p>
          </div>
        );
      })}
    </div>
  );
}

// ── Shared section label ───────────────────────────────────────────────────────

function SectionLabel({ label }: { label: string }) {
  return (
    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
      {label}
    </p>
  );
}
