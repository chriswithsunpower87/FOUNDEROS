/**
 * File: src/components/dashboard/EditIdeaModal.tsx
 * Purpose: Modal dialog for editing an existing DRAFT startup idea.
 * Responsibilities:
 *   - Pre-fill form with current idea data
 *   - Call PUT /ideas/{id} via useUpdateIdea hook
 *   - Only available when idea status is DRAFT
 * Dependencies:
 *   - react-hook-form, zod (validation)
 *   - hooks/useIdeas (useUpdateIdea)
 *   - types/idea.types (Idea)
 */

"use client";

import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { X } from "lucide-react";
import { useUpdateIdea } from "@/hooks/useIdeas";
import type { Idea } from "@/types/idea.types";

/** Validation schema — same rules as CreateIdeaModal */
const schema = z.object({
  title: z.string().min(3, "Title must be at least 3 characters").max(200),
  problem_statement: z
    .string()
    .min(10, "Please describe the problem in more detail"),
  target_audience: z.string().min(5, "Please describe your target audience"),
});

type FormValues = z.infer<typeof schema>;

interface EditIdeaModalProps {
  /** The idea to edit — its current field values pre-fill the form */
  idea: Idea;
  open: boolean;
  onClose: () => void;
}

/**
 * EditIdeaModal
 * Description: Modal form for editing an existing startup idea's metadata.
 * Only active when the idea status is DRAFT; blocked by the API otherwise.
 */
export function EditIdeaModal({ idea, open, onClose }: EditIdeaModalProps) {
  const { mutate: updateIdea, isPending } = useUpdateIdea(idea.id);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      title: idea.title,
      problem_statement: idea.problem_statement,
      target_audience: idea.target_audience,
    },
  });

  /**
   * Purpose: Re-sync form defaults if a different idea is opened.
   * Parameters:
   *   idea: The current idea whose values should populate the form.
   */
  useEffect(() => {
    reset({
      title: idea.title,
      problem_statement: idea.problem_statement,
      target_audience: idea.target_audience,
    });
  }, [idea, reset]);

  /**
   * Purpose: Submit updated idea data to the API.
   * Parameters:
   *   values: Validated form values.
   */
  function onSubmit(values: FormValues) {
    updateIdea(values, {
      onSuccess: () => {
        onClose();
      },
    });
  }

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-2xl shadow-xl w-full max-w-lg mx-4 p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">Edit Idea</h2>
            <p className="text-sm text-slate-500">
              Editing is only available while the idea is in DRAFT status
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Startup Name
            </label>
            <input
              {...register("title")}
              placeholder="e.g. AI Fitness App"
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {errors.title && (
              <p className="text-red-500 text-xs mt-1">{errors.title.message}</p>
            )}
          </div>

          {/* Problem Statement */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Problem Statement
            </label>
            <textarea
              {...register("problem_statement")}
              rows={3}
              placeholder="What problem does your startup solve? Be specific."
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            />
            {errors.problem_statement && (
              <p className="text-red-500 text-xs mt-1">
                {errors.problem_statement.message}
              </p>
            )}
          </div>

          {/* Target Audience */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Target Audience
            </label>
            <input
              {...register("target_audience")}
              placeholder="e.g. Busy professionals aged 25-40"
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {errors.target_audience && (
              <p className="text-red-500 text-xs mt-1">
                {errors.target_audience.message}
              </p>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 border border-slate-300 text-slate-700 py-2 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isPending}
              className="flex-1 bg-blue-500 hover:bg-blue-600 disabled:opacity-50 text-white py-2 rounded-lg text-sm font-medium transition-colors"
            >
              {isPending ? "Saving..." : "Save Changes"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
