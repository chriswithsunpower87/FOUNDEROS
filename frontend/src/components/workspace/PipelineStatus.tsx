/**
 * File: src/components/workspace/PipelineStatus.tsx
 * Purpose: Progress bar showing pipeline completion across all 10 agents.
 */

import type { IdeaStatus } from "@/types/idea.types";

interface PipelineStatusProps {
  total: number;
  completed: number;
  status: IdeaStatus;
}

export function PipelineStatus({ total, completed, status }: PipelineStatusProps) {
  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;

  if (status === "DRAFT") return null;

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-slate-700">
          {status === "COMPLETED"
            ? "Blueprint Complete"
            : status === "FAILED"
            ? "Pipeline Failed"
            : "Generating Blueprint..."}
        </span>
        <span className="text-sm font-semibold text-slate-900">
          {completed}/{total} agents
        </span>
      </div>
      <div className="w-full bg-slate-100 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-500 ${
            status === "COMPLETED"
              ? "bg-green-500"
              : status === "FAILED"
              ? "bg-red-500"
              : "bg-blue-500"
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {(status === "PROCESSING" || status === "PENDING") && (
        <p className="text-xs text-slate-400 mt-2">
          Agents are working in parallel — results appear as each completes
        </p>
      )}
    </div>
  );
}
