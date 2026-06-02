/**
 * File: src/components/workspace/IdeaHeader.tsx
 * Purpose: Displays idea metadata at the top of the workspace page.
 */

import { useAnalyzeIdea } from "@/hooks/useIdeas";
import { cn } from "@/lib/utils";
import { STATUS_COLORS } from "@/lib/constants";
import type { Idea } from "@/types/idea.types";
import { Play } from "lucide-react";

interface IdeaHeaderProps {
  idea: Idea;
}

export function IdeaHeader({ idea }: IdeaHeaderProps) {
  const { mutate: analyze, isPending } = useAnalyzeIdea();
  const canAnalyze = idea.status === "DRAFT" || idea.status === "FAILED";

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-2xl font-bold text-slate-900">{idea.title}</h1>
            <span
              className={cn(
                "inline-flex items-center text-xs font-medium px-2 py-0.5 rounded-full flex-shrink-0",
                STATUS_COLORS[idea.status]
              )}
            >
              {idea.status}
            </span>
          </div>

          <div className="space-y-2">
            <div>
              <span className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                Problem
              </span>
              <p className="text-sm text-slate-700 mt-0.5">
                {idea.problem_statement}
              </p>
            </div>
            <div>
              <span className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                Target Audience
              </span>
              <p className="text-sm text-slate-700 mt-0.5">{idea.target_audience}</p>
            </div>
          </div>
        </div>

        {/* Analyze button */}
        {canAnalyze && (
          <button
            onClick={() => analyze(idea.id)}
            disabled={isPending}
            className="flex-shrink-0 flex items-center gap-2 bg-blue-500 hover:bg-blue-600 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            <Play className="w-4 h-4" />
            {isPending ? "Starting..." : "Analyze"}
          </button>
        )}
      </div>
    </div>
  );
}
