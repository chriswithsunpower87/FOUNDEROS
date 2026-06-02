/**
 * File: src/components/workspace/AgentTraceView.tsx
 * Purpose: Displays detailed agent execution traces for the trace view feature.
 * Responsibilities:
 *   - Show each agent run with model used, tokens, duration
 *   - Expand to show the full prompt and output snapshot
 */

"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import type { AgentRun } from "@/types/report.types";

interface AgentTraceViewProps {
  traces: AgentRun[];
}

export function AgentTraceView({ traces }: AgentTraceViewProps) {
  if (traces.length === 0) {
    return (
      <div className="text-center py-12 text-slate-400 text-sm">
        Agent traces will appear here once the pipeline starts running.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {traces.map((trace) => (
        <TraceCard key={trace.id} trace={trace} />
      ))}
    </div>
  );
}

function TraceCard({ trace }: { trace: AgentRun }) {
  const [isOpen, setIsOpen] = useState(false);

  const duration =
    trace.started_at && trace.completed_at
      ? ((new Date(trace.completed_at).getTime() -
          new Date(trace.started_at).getTime()) /
          1000).toFixed(1)
      : null;

  return (
    <div className="bg-white rounded-xl border border-slate-200">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center gap-3 p-4 text-left"
      >
        <span
          className={`w-2 h-2 rounded-full flex-shrink-0 ${
            trace.status === "COMPLETED"
              ? "bg-green-500"
              : trace.status === "FAILED"
              ? "bg-red-500"
              : "bg-yellow-500"
          }`}
        />
        <span className="flex-1 text-sm font-medium text-slate-800">
          {trace.agent_name}
        </span>

        <div className="flex items-center gap-3 text-xs text-slate-400">
          {trace.model_used && <span>{trace.model_used}</span>}
          {trace.tokens_used && <span>{trace.tokens_used} tokens</span>}
          {duration && <span>{duration}s</span>}
        </div>

        {isOpen ? (
          <ChevronDown className="w-4 h-4 text-slate-400" />
        ) : (
          <ChevronRight className="w-4 h-4 text-slate-400" />
        )}
      </button>

      {isOpen && (
        <div className="border-t border-slate-100 p-4 space-y-4">
          {/* Prompt */}
          {trace.prompt_used && (
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
                Prompt Sent to LLM
              </p>
              <pre className="text-xs text-slate-600 bg-slate-50 rounded-lg p-3 overflow-auto max-h-48 whitespace-pre-wrap">
                {trace.prompt_used}
              </pre>
            </div>
          )}

          {/* Output */}
          {trace.output_snapshot && (
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
                Agent Output
              </p>
              <pre className="text-xs text-slate-600 bg-slate-50 rounded-lg p-3 overflow-auto max-h-48 whitespace-pre-wrap">
                {JSON.stringify(trace.output_snapshot, null, 2)}
              </pre>
            </div>
          )}

          {/* Error */}
          {trace.error_message && (
            <div className="bg-red-50 border border-red-200 text-red-600 text-xs p-3 rounded-lg">
              {trace.error_message}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
