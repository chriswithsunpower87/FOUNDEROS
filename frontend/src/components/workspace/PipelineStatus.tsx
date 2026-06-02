/**
 * File: src/components/workspace/PipelineStatus.tsx
 * Purpose: Visual progress bar showing pipeline completion across all 10 agents.
 */

import type { IdeaStatus } from "@/types/idea.types";

interface PipelineStatusProps {
  total: number;
  completed: number;
  status: IdeaStatus;
}

const AGENT_DOTS = [
  "📊","🔍","📋","🏗️","🗄️","🔌","🎨","🗺️","📣","⚠️"
];

export function PipelineStatus({ total, completed, status }: PipelineStatusProps) {
  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;

  if (status === "DRAFT") return null;

  const isRunning   = status === "PROCESSING" || status === "PENDING";
  const isDone      = status === "COMPLETED";
  const isFailed    = status === "FAILED";

  return (
    <div className={`rounded-xl border p-4 transition-all ${
      isDone    ? "bg-green-50 border-green-200" :
      isFailed  ? "bg-red-50 border-red-200"     :
                  "bg-blue-50 border-blue-200"
    }`}>
      {/* Top row */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-base">
            {isDone ? "✅" : isFailed ? "❌" : "⚙️"}
          </span>
          <span className={`text-sm font-semibold ${
            isDone   ? "text-green-800" :
            isFailed ? "text-red-700"   :
                       "text-blue-800"
          }`}>
            {isDone    ? "Blueprint Complete — all 10 agents done!"  :
             isFailed  ? "Pipeline encountered an error"             :
                         "Generating your startup blueprint…"}
          </span>
        </div>
        <span className={`text-sm font-bold tabular-nums ${
          isDone   ? "text-green-700" :
          isFailed ? "text-red-600"   :
                     "text-blue-700"
        }`}>
          {completed}/{total}
        </span>
      </div>

      {/* Progress bar */}
      <div className={`w-full rounded-full h-2.5 mb-3 ${
        isDone   ? "bg-green-200" :
        isFailed ? "bg-red-200"   :
                   "bg-blue-200"
      }`}>
        <div
          className={`h-2.5 rounded-full transition-all duration-700 ease-out ${
            isDone   ? "bg-green-500" :
            isFailed ? "bg-red-500"   :
                       "bg-blue-500"
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>

      {/* Agent dot indicators */}
      <div className="flex gap-1.5">
        {AGENT_DOTS.map((emoji, i) => (
          <div
            key={i}
            title={`Agent ${i + 1}`}
            className={`flex-1 h-8 rounded-lg flex items-center justify-center text-sm transition-all duration-300 ${
              i < completed
                ? isDone ? "bg-green-100" : "bg-blue-100"
                : "bg-white/60"
            }`}
          >
            <span className={i < completed ? "opacity-100" : "opacity-30"}>
              {emoji}
            </span>
          </div>
        ))}
      </div>

      {isRunning && (
        <p className="text-xs text-blue-600 mt-2 text-center">
          Each agent reads the previous one&apos;s output — results appear as they complete
        </p>
      )}
    </div>
  );
}
