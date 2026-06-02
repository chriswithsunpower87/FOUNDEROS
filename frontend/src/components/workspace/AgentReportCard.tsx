/**
 * File: src/components/workspace/AgentReportCard.tsx
 * Purpose: Collapsible card showing one agent's status and output.
 * Responsibilities:
 *   - Show agent name, status badge, and execution time
 *   - Expand to show structured JSON output in readable format
 *   - Show spinner while RUNNING, error message if FAILED
 */

"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight, Loader2, CheckCircle, XCircle, Clock } from "lucide-react";
import { AGENT_LABELS } from "@/lib/constants";
import { cn } from "@/lib/utils";
import type { Report } from "@/types/report.types";

interface AgentReportCardProps {
  agentType: string;
  report: Report | null;
}

export function AgentReportCard({ agentType, report }: AgentReportCardProps) {
  const [isOpen, setIsOpen] = useState(false);
  const label = AGENT_LABELS[agentType] ?? agentType;
  const status = report?.status ?? "PENDING";

  const statusIcon = {
    PENDING: <Clock className="w-4 h-4 text-slate-400" />,
    RUNNING: <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />,
    COMPLETED: <CheckCircle className="w-4 h-4 text-green-500" />,
    FAILED: <XCircle className="w-4 h-4 text-red-500" />,
  }[status];

  const isExpandable = status === "COMPLETED" && report?.output;

  return (
    <div
      className={cn(
        "bg-white rounded-xl border transition-all",
        status === "RUNNING" ? "border-blue-200" : "border-slate-200",
        status === "COMPLETED" ? "hover:shadow-sm" : ""
      )}
    >
      {/* Header */}
      <button
        onClick={() => isExpandable && setIsOpen(!isOpen)}
        className={cn(
          "w-full flex items-center gap-3 p-4 text-left",
          isExpandable ? "cursor-pointer" : "cursor-default"
        )}
      >
        {statusIcon}
        <span className="flex-1 text-sm font-medium text-slate-800">{label}</span>

        {report?.execution_time_ms && (
          <span className="text-xs text-slate-400">
            {(report.execution_time_ms / 1000).toFixed(1)}s
          </span>
        )}

        {isExpandable && (
          <span className="text-slate-400">
            {isOpen ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
          </span>
        )}
      </button>

      {/* Error message */}
      {status === "FAILED" && report?.error_message && (
        <div className="px-4 pb-4">
          <div className="bg-red-50 border border-red-200 text-red-600 text-xs p-3 rounded-lg">
            {report.error_message}
          </div>
        </div>
      )}

      {/* Expanded output */}
      {isOpen && report?.output && (
        <div className="border-t border-slate-100 px-4 pb-4 pt-3">
          {report.reasoning_summary && (
            <p className="text-xs text-slate-500 italic mb-3">
              {report.reasoning_summary}
            </p>
          )}
          <OutputRenderer output={report.output} />
        </div>
      )}
    </div>
  );
}

/** Recursively render agent output as readable key-value pairs */
function OutputRenderer({ output }: { output: Record<string, unknown> }) {
  return (
    <div className="space-y-3">
      {Object.entries(output).map(([key, value]) => (
        <OutputField key={key} fieldKey={key} value={value} />
      ))}
    </div>
  );
}

function OutputField({ fieldKey, value }: { fieldKey: string; value: unknown }) {
  const label = fieldKey.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

  if (Array.isArray(value)) {
    return (
      <div>
        <p className="text-xs font-semibold text-slate-600 mb-1">{label}</p>
        <ul className="space-y-1">
          {value.map((item, i) => (
            <li key={i} className="text-sm text-slate-700">
              {typeof item === "object" ? (
                <div className="bg-slate-50 rounded-lg p-2 space-y-1">
                  {Object.entries(item as Record<string, unknown>).map(([k, v]) => (
                    <div key={k}>
                      <span className="text-xs font-medium text-slate-500">
                        {k.replace(/_/g, " ")}:{" "}
                      </span>
                      <span className="text-xs text-slate-700">{String(v)}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <span className="flex gap-1.5">
                  <span className="text-blue-400 mt-0.5">•</span>
                  {String(item)}
                </span>
              )}
            </li>
          ))}
        </ul>
      </div>
    );
  }

  if (typeof value === "object" && value !== null) {
    return (
      <div>
        <p className="text-xs font-semibold text-slate-600 mb-1">{label}</p>
        <div className="bg-slate-50 rounded-lg p-2 space-y-1">
          {Object.entries(value as Record<string, unknown>).map(([k, v]) => (
            <div key={k}>
              <span className="text-xs font-medium text-slate-500">
                {k.replace(/_/g, " ")}:{" "}
              </span>
              <span className="text-xs text-slate-700">{String(v)}</span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div>
      <p className="text-xs font-semibold text-slate-600 mb-0.5">{label}</p>
      <p className="text-sm text-slate-700 leading-relaxed">{String(value)}</p>
    </div>
  );
}
