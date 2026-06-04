/**
 * File: src/hooks/useSSE.ts
 * Purpose: Real-time agent progress via Server-Sent Events (SSE).
 * Responsibilities:
 *   - Open an EventSource connection to /ideas/{id}/stream when the
 *     pipeline is running (PENDING or PROCESSING status)
 *   - Patch the React Query reports cache on each SSE event so the UI
 *     updates instantly without polling
 *   - Close the connection automatically when all agents finish or on unmount
 *   - Fall back to React Query polling if SSE is unsupported or fails
 * Dependencies:
 *   - @tanstack/react-query (useQueryClient)
 *   - lib/constants (API_BASE_URL)
 *   - types/report.types (Report)
 *   - types/idea.types (IdeaStatus)
 */

"use client";

import { useEffect, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { API_BASE_URL } from "@/lib/constants";
import type { IdeaStatus } from "@/types/idea.types";
import type { Report } from "@/types/report.types";

interface UseSSEOptions {
  ideaId: string;
  /** Current idea status — SSE only opens when the pipeline is active */
  ideaStatus: IdeaStatus | undefined;
}

/**
 * useSSE
 * Description: Subscribes to the backend SSE stream for an idea's agent progress.
 *   Patches the React Query ['reports', ideaId] cache on every SSE message,
 *   giving the workspace page instant updates (< 500ms) instead of 3-second polling.
 *
 * SSE Authentication:
 *   The browser's EventSource API cannot send custom headers, so the JWT
 *   is passed as a query parameter. The backend validates it before streaming.
 */
export function useSSE({ ideaId, ideaStatus }: UseSSEOptions): void {
  const queryClient = useQueryClient();
  const sourceRef = useRef<EventSource | null>(null);

  const isRunning = ideaStatus === "PENDING" || ideaStatus === "PROCESSING";

  useEffect(() => {
    // Only open SSE when the pipeline is active and the browser supports it
    if (!isRunning || !ideaId || typeof EventSource === "undefined") return;

    const token = localStorage.getItem("access_token");
    if (!token) return;

    const url = `${API_BASE_URL}/api/v1/ideas/${ideaId}/stream?token=${encodeURIComponent(token)}`;
    const source = new EventSource(url);
    sourceRef.current = source;

    /**
     * Purpose: Handle each SSE event from the backend.
     *   Either patches the reports cache or triggers final invalidation.
     * Parameters:
     *   event: MessageEvent with JSON-stringified report data.
     */
    source.onmessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data as string) as Record<string, unknown>;

        // Final event — invalidate everything and close
        if (data.type === "done" || data.type === "timeout") {
          source.close();
          queryClient.invalidateQueries({ queryKey: ["idea", ideaId] });
          queryClient.invalidateQueries({ queryKey: ["reports", ideaId] });
          return;
        }

        // Report update event — patch the cache entry for this agent
        queryClient.setQueryData(
          ["reports", ideaId],
          (old: Report[] | undefined) => {
            if (!old) {
              // First event — create the array with this report
              return [data as unknown as Report];
            }

            const idx = old.findIndex(
              (r) => r.agent_type === (data.agent_type as string)
            );

            if (idx >= 0) {
              // Update existing report
              const updated = [...old];
              updated[idx] = { ...updated[idx], ...(data as Partial<Report>) };
              return updated;
            }

            // New report (first time this agent appears in the cache)
            return [...old, data as unknown as Report];
          }
        );
      } catch {
        // Non-fatal — malformed event from backend, ignore
      }
    };

    /**
     * Purpose: Handle SSE connection errors.
     *   Close cleanly; React Query polling will take over.
     */
    source.onerror = () => {
      source.close();
      sourceRef.current = null;
    };

    // Cleanup: close connection on unmount or when status changes
    return () => {
      source.close();
      sourceRef.current = null;
    };
  }, [ideaId, isRunning, queryClient]);
}
