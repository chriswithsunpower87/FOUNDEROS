/**
 * File: src/hooks/useReports.ts
 * Purpose: React Query hooks for fetching reports and trace data.
 * Responsibilities:
 *   - Poll /reports every 3 seconds while pipeline is running
 *   - Stop polling when all reports are COMPLETED or FAILED
 *   - Fetch agent trace data for the trace view
 */

"use client";

import { useQuery } from "@tanstack/react-query";
import { reportService } from "@/services/reportService";
import { REPORTS_POLL_INTERVAL_MS } from "@/lib/constants";
import type { Report } from "@/types/report.types";

/**
 * Check if the pipeline is still running (any report is PENDING or RUNNING).
 */
function isPipelineRunning(reports: Report[]): boolean {
  if (reports.length === 0) return false;
  return reports.some((r) => r.status === "PENDING" || r.status === "RUNNING");
}

/**
 * Fetch and poll agent reports for an idea.
 * Polling interval is 3 seconds, stops automatically when done.
 * @param ideaId - UUID of the idea
 */
export function useReports(ideaId: string) {
  return useQuery({
    queryKey: ["reports", ideaId],
    queryFn: () => reportService.getReports(ideaId),
    enabled: !!ideaId,
    // Refetch every 3 seconds while pipeline is running
    refetchInterval: (query) => {
      const data = query.state.data;
      if (!data) return REPORTS_POLL_INTERVAL_MS;
      return isPipelineRunning(data) ? REPORTS_POLL_INTERVAL_MS : false;
    },
    staleTime: 1000,
  });
}

/**
 * Fetch agent run traces for the trace view.
 * @param ideaId - UUID of the idea
 */
export function useAgentTrace(ideaId: string) {
  return useQuery({
    queryKey: ["trace", ideaId],
    queryFn: () => reportService.getTrace(ideaId),
    enabled: !!ideaId,
    staleTime: 60_000,
  });
}
