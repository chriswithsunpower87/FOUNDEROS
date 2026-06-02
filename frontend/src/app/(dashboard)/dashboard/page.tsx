/**
 * File: src/app/(dashboard)/dashboard/page.tsx
 * Purpose: Dashboard page — displays all the user's startup ideas.
 */

"use client";

import { useState } from "react";
import { Plus } from "lucide-react";
import { IdeaList } from "@/components/dashboard/IdeaList";
import { CreateIdeaModal } from "@/components/dashboard/CreateIdeaModal";
import { useIdeas } from "@/hooks/useIdeas";

export default function DashboardPage() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const { data, isLoading, error } = useIdeas();

  const ideas = data?.items ?? [];

  return (
    <div className="max-w-6xl mx-auto">
      {/* Page header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">My Ideas</h1>
          <p className="text-slate-500 text-sm mt-1">
            {ideas.length} idea{ideas.length !== 1 ? "s" : ""} — each one a
            potential startup blueprint
          </p>
        </div>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="inline-flex items-center gap-2 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Idea
        </button>
      </div>

      {/* Error state */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 mb-6 text-sm">
          Failed to load ideas. Please refresh the page.
        </div>
      )}

      {/* Ideas grid */}
      <IdeaList ideas={ideas} isLoading={isLoading} />

      {/* Create modal */}
      <CreateIdeaModal
        open={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
      />
    </div>
  );
}
