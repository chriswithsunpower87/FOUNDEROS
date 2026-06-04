/**
 * File: src/components/dashboard/IdeaCard.tsx
 * Purpose: Single idea card shown in the dashboard grid.
 * Responsibilities:
 *   - Display idea title, status badge, and metadata
 *   - Provide View and Delete action buttons
 */

"use client";

import { useState } from "react";
import Link from "next/link";
import { Trash2, ArrowRight, Clock, Pencil } from "lucide-react";
import { cn, formatDate, truncate } from "@/lib/utils";
import { STATUS_COLORS } from "@/lib/constants";
import { useDeleteIdea } from "@/hooks/useIdeas";
import { EditIdeaModal } from "./EditIdeaModal";
import type { Idea } from "@/types/idea.types";

interface IdeaCardProps {
  idea: Idea;
}

export function IdeaCard({ idea }: IdeaCardProps) {
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const { mutate: deleteIdea, isPending } = useDeleteIdea();

  function handleDelete() {
    if (confirmDelete) {
      deleteIdea(idea.id);
    } else {
      setConfirmDelete(true);
      // Auto-reset confirmation after 3 seconds
      setTimeout(() => setConfirmDelete(false), 3000);
    }
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 hover:shadow-md transition-shadow">
      {/* Status badge + action buttons */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <span
          className={cn(
            "inline-flex items-center text-xs font-medium px-2 py-0.5 rounded-full",
            STATUS_COLORS[idea.status]
          )}
        >
          {idea.status === "PROCESSING" && (
            <span className="w-1.5 h-1.5 bg-current rounded-full mr-1.5 animate-pulse" />
          )}
          {idea.status}
        </span>

        <div className="flex items-center gap-2">
          {/* Edit button — only visible for DRAFT ideas */}
          {idea.status === "DRAFT" && (
            <button
              onClick={() => setIsEditOpen(true)}
              className="text-slate-400 hover:text-blue-500 transition-colors"
              title="Edit idea"
            >
              <Pencil className="w-3.5 h-3.5" />
            </button>
          )}

          {/* Delete button with 2-click confirmation */}
          <button
            onClick={handleDelete}
            disabled={isPending}
            className={cn(
              "text-xs transition-colors",
              confirmDelete
                ? "text-red-600 font-medium"
                : "text-slate-400 hover:text-red-500"
            )}
          >
            {isPending ? (
              "Deleting..."
            ) : confirmDelete ? (
              "Confirm?"
            ) : (
              <Trash2 className="w-3.5 h-3.5" />
            )}
          </button>
        </div>
      </div>

      {/* Title */}
      <h3 className="text-base font-semibold text-slate-900 mb-1">
        {idea.title}
      </h3>

      {/* Problem statement preview */}
      <p className="text-sm text-slate-500 leading-relaxed mb-4">
        {truncate(idea.problem_statement, 120)}
      </p>

      {/* Footer */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1 text-xs text-slate-400">
          <Clock className="w-3 h-3" />
          {formatDate(idea.created_at)}
        </div>
        <Link
          href={`/ideas/${idea.id}`}
          className="inline-flex items-center gap-1 text-xs font-medium text-blue-500 hover:text-blue-600 transition-colors"
        >
          View Blueprint
          <ArrowRight className="w-3 h-3" />
        </Link>
      </div>

      {/* Edit modal — only mounted when open to save memory */}
      <EditIdeaModal
        idea={idea}
        open={isEditOpen}
        onClose={() => setIsEditOpen(false)}
      />
    </div>
  );
}
