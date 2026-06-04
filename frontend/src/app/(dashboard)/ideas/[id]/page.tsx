/**
 * File: src/app/(dashboard)/ideas/[id]/page.tsx
 * Purpose: Idea workspace page — agent reports, trace view, version history.
 * Responsibilities:
 *   - Display idea metadata + Analyze button
 *   - Real-time agent progress via SSE (falls back to React Query polling)
 *   - Version picker to browse past analysis runs
 *   - Export + Share buttons when blueprint is complete
 */

"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import { useIdea } from "@/hooks/useIdeas";
import { useReports, useAgentTrace, useVersions } from "@/hooks/useReports";
import { useSSE } from "@/hooks/useSSE";
import { IdeaHeader } from "@/components/workspace/IdeaHeader";
import { PipelineStatus } from "@/components/workspace/PipelineStatus";
import { AgentReportCard } from "@/components/workspace/AgentReportCard";
import { AgentTraceView } from "@/components/workspace/AgentTraceView";
import { ExportButtons } from "@/components/workspace/ExportButtons";
import { ShareButton } from "@/components/workspace/ShareButton";
import { VersionPicker } from "@/components/workspace/VersionPicker";
import { AGENT_ORDER } from "@/lib/constants";
import type { Report } from "@/types/report.types";

type ActiveTab = "reports" | "trace";

export default function IdeaWorkspacePage() {
  const params = useParams();
  const ideaId = params.id as string;
  const [activeTab, setActiveTab] = useState<ActiveTab>("reports");

  // null = latest version (live); number = viewing a historical version
  const [selectedVersion, setSelectedVersion] = useState<number | undefined>(undefined);

  const { data: idea, isLoading: ideaLoading } = useIdea(ideaId);
  const { data: versions = [] } = useVersions(ideaId);
  const { data: reports = [] } = useReports(ideaId, selectedVersion);
  const { data: traces = [] } = useAgentTrace(ideaId);

  // SSE: real-time updates while pipeline is running (latest version only)
  useSSE({ ideaId, ideaStatus: selectedVersion ? undefined : idea?.status });

  const reportMap = reports.reduce<Record<string, Report>>((acc, r) => {
    acc[r.agent_type] = r;
    return acc;
  }, {});

  const completedCount = reports.filter((r) => r.status === "COMPLETED").length;
  const latestVersion = idea?.analysis_count ?? 1;

  // The "effective" status for the pipeline bar:
  // - When viewing a historical version, always show COMPLETED
  // - Otherwise show the live idea status
  const displayStatus = selectedVersion
    ? "COMPLETED"
    : idea?.status;

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

  const isViewingLatest = !selectedVersion || selectedVersion === latestVersion;

  return (
    <div className="max-w-4xl mx-auto">
      {/* Idea metadata + Analyze/Re-analyze button */}
      <IdeaHeader idea={idea} />

      {/* Pipeline progress bar — reflects the version being viewed */}
      <div className="mt-6 mb-4">
        <PipelineStatus
          total={11}
          completed={completedCount}
          status={displayStatus ?? "DRAFT"}
        />
      </div>

      {/* Version picker — only shown when there are multiple runs */}
      {versions.length > 1 && (
        <div className="mb-4">
          <VersionPicker
            versions={versions}
            selectedVersion={selectedVersion ?? latestVersion}
            latestVersion={latestVersion}
            onSelect={(v) =>
              setSelectedVersion(v === latestVersion ? undefined : v)
            }
          />
        </div>
      )}

      {/* Export + Share — only for latest completed blueprint */}
      {isViewingLatest && idea.status === "COMPLETED" && (
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

      {activeTab === "trace" && <AgentTraceView traces={traces} />}
    </div>
  );
}
