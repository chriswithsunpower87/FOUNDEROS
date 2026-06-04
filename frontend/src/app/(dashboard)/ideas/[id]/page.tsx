/**
 * File: src/app/(dashboard)/ideas/[id]/page.tsx
 * Purpose: Idea workspace page — shows agent reports + trace view.
 * Responsibilities:
 *   - Display idea metadata (title, problem, audience)
 *   - Show all 11 agent report cards with REAL-TIME updates via SSE
 *   - Fall back to React Query polling if SSE is unavailable
 *   - Show Agent Trace View tab and Export buttons when complete
 *   - Show Share button for public blueprint links
 */

"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import { useIdea } from "@/hooks/useIdeas";
import { useReports, useAgentTrace } from "@/hooks/useReports";
import { useSSE } from "@/hooks/useSSE";
import { IdeaHeader } from "@/components/workspace/IdeaHeader";
import { PipelineStatus } from "@/components/workspace/PipelineStatus";
import { AgentReportCard } from "@/components/workspace/AgentReportCard";
import { AgentTraceView } from "@/components/workspace/AgentTraceView";
import { ExportButtons } from "@/components/workspace/ExportButtons";
import { ShareButton } from "@/components/workspace/ShareButton";
import { AGENT_ORDER } from "@/lib/constants";
import type { Report } from "@/types/report.types";

type ActiveTab = "reports" | "trace";

export default function IdeaWorkspacePage() {
  const params = useParams();
  const ideaId = params.id as string;
  const [activeTab, setActiveTab] = useState<ActiveTab>("reports");

  const { data: idea, isLoading: ideaLoading } = useIdea(ideaId);
  const { data: reports = [] } = useReports(ideaId);
  const { data: traces = [] } = useAgentTrace(ideaId);

  // SSE: pushes report updates in real time while the pipeline runs.
  // Falls back to React Query polling (useReports) automatically if SSE fails.
  useSSE({ ideaId, ideaStatus: idea?.status });

  // Build a map of agent_type → report for O(1) lookup in render
  const reportMap = reports.reduce<Record<string, Report>>((acc, r) => {
    acc[r.agent_type] = r;
    return acc;
  }, {});

  const completedCount = reports.filter((r) => r.status === "COMPLETED").length;

  if (ideaLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
      </div>
    );
  }

  if (!idea) {
    return (
      <div className="text-center text-slate-500 mt-20">Idea not found.</div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Idea metadata + Analyze button */}
      <IdeaHeader idea={idea} />

      {/* Pipeline progress bar */}
      <div className="mt-6 mb-4">
        <PipelineStatus
          total={11}
          completed={completedCount}
          status={idea.status}
        />
      </div>

      {/* Export + Share — only when blueprint is complete */}
      {idea.status === "COMPLETED" && (
        <div className="mb-6 space-y-3">
          <ExportButtons ideaId={ideaId} ideaTitle={idea.title} />
          <ShareButton ideaId={ideaId} isPublic={idea.is_public ?? false} />
        </div>
      )}

      {/* Tab switcher */}
      <div className="flex gap-1 bg-slate-100 p-1 rounded-lg w-fit mb-6">
        <button
          onClick={() => setActiveTab("reports")}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === "reports"
              ? "bg-white text-slate-900 shadow-sm"
              : "text-slate-500 hover:text-slate-700"
          }`}
        >
          Reports
        </button>
        <button
          onClick={() => setActiveTab("trace")}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === "trace"
              ? "bg-white text-slate-900 shadow-sm"
              : "text-slate-500 hover:text-slate-700"
          }`}
        >
          Agent Trace
        </button>
      </div>

      {/* Reports tab */}
      {activeTab === "reports" && (
        <div className="space-y-3">
          {AGENT_ORDER.map((agentType) => (
            <AgentReportCard
              key={agentType}
              agentType={agentType}
              report={reportMap[agentType] ?? null}
            />
          ))}
        </div>
      )}

      {/* Trace view tab */}
      {activeTab === "trace" && <AgentTraceView traces={traces} />}
    </div>
  );
}
