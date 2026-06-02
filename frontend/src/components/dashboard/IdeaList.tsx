/**
 * File: src/components/dashboard/IdeaList.tsx
 * Purpose: Grid of IdeaCards with loading skeletons and empty state.
 */

import { IdeaCard } from "./IdeaCard";
import type { Idea } from "@/types/idea.types";
import { Lightbulb } from "lucide-react";

interface IdeaListProps {
  ideas: Idea[];
  isLoading: boolean;
}

export function IdeaList({ ideas, isLoading }: IdeaListProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <div
            key={i}
            className="bg-white rounded-xl border border-slate-200 p-5 animate-pulse"
          >
            <div className="h-5 bg-slate-100 rounded w-16 mb-3" />
            <div className="h-5 bg-slate-100 rounded w-3/4 mb-2" />
            <div className="h-4 bg-slate-100 rounded w-full mb-1" />
            <div className="h-4 bg-slate-100 rounded w-5/6 mb-4" />
            <div className="h-4 bg-slate-100 rounded w-1/3" />
          </div>
        ))}
      </div>
    );
  }

  if (ideas.length === 0) {
    return (
      <div className="text-center py-20 bg-white rounded-xl border border-dashed border-slate-300">
        <Lightbulb className="w-10 h-10 text-slate-300 mx-auto mb-3" />
        <h3 className="text-slate-600 font-medium mb-1">No ideas yet</h3>
        <p className="text-slate-400 text-sm">
          Click &quot;New Idea&quot; to create your first startup blueprint
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {ideas.map((idea) => (
        <IdeaCard key={idea.id} idea={idea} />
      ))}
    </div>
  );
}
