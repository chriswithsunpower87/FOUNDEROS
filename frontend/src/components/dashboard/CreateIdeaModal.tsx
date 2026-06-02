/**
 * File: src/components/dashboard/CreateIdeaModal.tsx
 * Purpose: Modal dialog for creating a new startup idea.
 */

"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { X } from "lucide-react";
import { useCreateIdea } from "@/hooks/useIdeas";
import type { CreateIdeaPayload } from "@/types/idea.types";

const schema = z.object({
  title: z.string().min(3, "Title must be at least 3 characters").max(200),
  problem_statement: z.string().min(10, "Please describe the problem in more detail"),
  target_audience: z.string().min(5, "Please describe your target audience"),
});

type FormValues = z.infer<typeof schema>;

interface CreateIdeaModalProps {
  open: boolean;
  onClose: () => void;
}

export function CreateIdeaModal({ open, onClose }: CreateIdeaModalProps) {
  const { mutate: createIdea, isPending } = useCreateIdea();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  function onSubmit(values: FormValues) {
    createIdea(values as CreateIdeaPayload, {
      onSuccess: () => {
        reset();
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
        <div className="flex items-center justify-between mb-5">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">New Startup Idea</h2>
            <p className="text-sm text-slate-500">
              Our AI agents will build a complete blueprint from this
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
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
              {isPending ? "Creating..." : "Create Idea"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
