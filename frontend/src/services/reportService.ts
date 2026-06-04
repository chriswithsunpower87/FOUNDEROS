/**
 * File: src/services/reportService.ts
 * Purpose: API calls for fetching agent reports, traces, and exports.
 */

import api from "./api";
import type { AgentRun, Report } from "@/types/report.types";
import type { APIResponse } from "@/types/api.types";
import { API_BASE_URL } from "@/lib/constants";

export const reportService = {
  /**
   * Get agent reports for an idea, optionally filtered by analysis version.
   * @param ideaId - UUID of the idea
   * @param version - Analysis version (omit for latest)
   */
  async getReports(ideaId: string, version?: number): Promise<Report[]> {
    const url = version
      ? `/ideas/${ideaId}/reports?version=${version}`
      : `/ideas/${ideaId}/reports`;
    const response = await api.get<APIResponse<Report[]>>(url);
    return response.data.data;
  },

  /**
   * Get all available analysis version numbers for an idea.
   * Returns e.g. [1, 2, 3] if analyzed three times.
   * @param ideaId - UUID of the idea
   */
  async getVersions(ideaId: string): Promise<number[]> {
    const response = await api.get<APIResponse<number[]>>(
      `/ideas/${ideaId}/versions`
    );
    return response.data.data;
  },

  /**
   * Get all agent run traces for the trace view.
   * @param ideaId - UUID of the idea
   */
  async getTrace(ideaId: string): Promise<AgentRun[]> {
    const response = await api.get<APIResponse<AgentRun[]>>(
      `/ideas/${ideaId}/trace`
    );
    return response.data.data;
  },

  /**
   * Download the full blueprint as a PDF file.
   * Uses fetch() + Authorization header because a plain <a> tag cannot
   * send custom headers — the export endpoint requires a valid JWT.
   * @param ideaId - UUID of the idea
   * @param title - Idea title (used for filename)
   */
  async downloadPDF(ideaId: string, title: string): Promise<void> {
    const token = localStorage.getItem("access_token");
    const url = `${API_BASE_URL}/api/v1/ideas/${ideaId}/export/pdf`;

    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) {
      throw new Error(`PDF export failed: ${response.statusText}`);
    }

    // Convert to blob, create a temporary object URL, trigger click, then clean up
    const blob = await response.blob();
    const objectUrl = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = objectUrl;
    link.download = `${title.toLowerCase().replace(/ /g, "-")}-blueprint.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(objectUrl);
  },

  /**
   * Download the full blueprint as a Markdown file.
   * Uses fetch() + Authorization header for the same reason as downloadPDF.
   * @param ideaId - UUID of the idea
   * @param title - Idea title (used for filename)
   */
  async downloadMarkdown(ideaId: string, title: string): Promise<void> {
    const token = localStorage.getItem("access_token");
    const url = `${API_BASE_URL}/api/v1/ideas/${ideaId}/export/markdown`;

    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) {
      throw new Error(`Markdown export failed: ${response.statusText}`);
    }

    const blob = await response.blob();
    const objectUrl = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = objectUrl;
    link.download = `${title.toLowerCase().replace(/ /g, "-")}-blueprint.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(objectUrl);
  },
};
