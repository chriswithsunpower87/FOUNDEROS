/**
 * File: src/hooks/useIdeas.ts
 * Purpose: React Query hooks for idea CRUD operations.
 * Responsibilities:
 *   - Fetch, create, update, delete ideas via React Query
 *   - Automatically invalidate cache on mutations
 */

"use client";

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { ideaService } from "@/services/ideaService";
import type { CreateIdeaPayload } from "@/types/idea.types";

/** Query key for the ideas list */
const IDEAS_KEY = ["ideas"];

/**
 * Fetch all ideas for the current user.
 */
export function useIdeas() {
  return useQuery({
    queryKey: IDEAS_KEY,
    queryFn: () => ideaService.listIdeas(),
    staleTime: 30_000,
  });
}

/**
 * Fetch a single idea by ID.
 * @param ideaId - UUID of the idea
 */
export function useIdea(ideaId: string) {
  return useQuery({
    queryKey: ["idea", ideaId],
    queryFn: () => ideaService.getIdea(ideaId),
    enabled: !!ideaId,
    staleTime: 30_000,
  });
}

/**
 * Create a new idea mutation.
 * Invalidates the ideas list on success.
 */
export function useCreateIdea() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateIdeaPayload) => ideaService.createIdea(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: IDEAS_KEY }),
  });
}

/**
 * Delete an idea mutation.
 * Invalidates the ideas list on success.
 * @param ideaId - UUID of the idea to delete
 */
export function useDeleteIdea() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (ideaId: string) => ideaService.deleteIdea(ideaId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: IDEAS_KEY }),
  });
}

/**
 * Trigger the AI analysis pipeline for an idea.
 * Invalidates the idea and ideas list on success.
 */
export function useAnalyzeIdea() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (ideaId: string) => ideaService.analyzeIdea(ideaId),
    onSuccess: (_data, ideaId) => {
      queryClient.invalidateQueries({ queryKey: ["idea", ideaId] });
      queryClient.invalidateQueries({ queryKey: IDEAS_KEY });
    },
  });
}
