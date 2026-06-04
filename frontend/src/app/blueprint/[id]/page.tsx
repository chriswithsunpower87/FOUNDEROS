/**
 * File: src/app/blueprint/[id]/page.tsx
 * Purpose: Public read-only blueprint page — no login required.
 * Responsibilities:
 *   - Fetch the public blueprint from GET /public/blueprints/{id}
 *   - Render all agent report cards in read-only mode
 *   - Show a CTA to sign up and create your own blueprint
 */

"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { AgentReportCard } from "@/components/workspace/AgentReportCard";
import { API_BASE_URL, AGENT_ORDER } from "@/lib/constants";
import type { Idea } from "@/types/idea.types";
import type { Report } from "@/types/report.types";

interface PublicBlueprint {
  idea: Idea;
  reports: Report[];
}

export default function PublicBlueprintPage() {
  const params = useParams();
  const ideaId = params.id as string;

  const [data, setData] = useState<PublicBlueprint | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/v1/public/blueprints/${ideaId}`)
      .then((res) => {
        if (!res.ok) throw new Error("Not found");
        return res.json();
      })
      .then((json) => setData(json.data as PublicBlueprint))
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, [ideaId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center gap-4">
        <p className="text-slate-500">This blueprint is private or doesn&apos;t exist.</p>
        <Link href="/" className="text-blue-500 hover:underline text-sm">
          Create your own on FounderOS →
        </Link>
      </div>
    );
  }

  const { idea, reports } = data;
  const reportMap = reports.reduce<Record<string, Report>>((acc, r) => {
    acc[r.agent_type] = r;
    return acc;
  }, {});

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Public header banner */}
      <div className="bg-white border-b border-slate-200 px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <span className="text-xl font-bold text-slate-900 tracking-tight">
            Founder<span className="text-blue-500">OS</span>
          </span>
          <Link
            href="/register"
            className="bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            Build Your Own Blueprint →
          </Link>
        </div>
      </div>

      <main className="max-w-4xl mx-auto px-6 py-8">
        {/* Idea metadata */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 mb-6">
          <p className="text-xs text-slate-400 uppercase tracking-wide font-medium mb-1">
            Public Startup Blueprint
          </p>
          <h1 className="text-2xl font-bold text-slate-900 mb-3">{idea.title}</h1>
          <div className="space-y-2">
            <div>
              <span className="text-xs font-medium text-slate-500 uppercase tracking-wide">Problem</span>
              <p className="text-sm text-slate-700 mt-0.5">{idea.problem_statement}</p>
            </div>
            <div>
              <span className="text-xs font-medium text-slate-500 uppercase tracking-wide">Target Audience</span>
              <p className="text-sm text-slate-700 mt-0.5">{idea.target_audience}</p>
            </div>
          </div>
        </div>

        {/* All 11 agent reports */}
        <div className="space-y-3">
          {AGENT_ORDER.map((agentType) => (
            <AgentReportCard
              key={agentType}
              agentType={agentType}
              report={reportMap[agentType] ?? null}
            />
          ))}
        </div>

        {/* CTA footer */}
        <div className="mt-10 text-center bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-8 text-white">
          <p className="text-xl font-bold mb-2">Got a startup idea?</p>
          <p className="text-blue-100 text-sm mb-5">
            FounderOS turns any idea into a complete startup blueprint in minutes — 11 AI agents, zero cost.
          </p>
          <Link
            href="/register"
            className="inline-block bg-white text-blue-600 font-semibold px-6 py-2.5 rounded-xl hover:shadow-md transition-all"
          >
            Get Started Free →
          </Link>
        </div>
      </main>
    </div>
  );
}
