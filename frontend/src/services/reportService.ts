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
   * Get all agent reports for an idea.
   * Called every 3 seconds during pipeline execution.
   * @param ideaId - UUID of the idea
   */
  async getReports(ideaId: string): Promise<Report[]> {
    const response = await api.get<APIResponse<Report[]>>(
      `/ideas/${ideaId}/reports`
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
   * @param ideaId - UUID of the idea
   * @param title - Idea title (used for filename)
   */
  downloadPDF(ideaId: string, title: string): void {
    const token = localStorage.getItem("access_token");
    const url = `${API_BASE_URL}/api/v1/ideas/${ideaId}/export/pdf`;
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute(
      "download",
      `${title.toLowerCase().replace(/ /g, "-")}-blueprint.pdf`
    );
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  },

  /**
   * Download the full blueprint as a Markdown file.
   * @param ideaId - UUID of the idea
   * @param title - Idea title (used for filename)
   */
  downloadMarkdown(ideaId: string, title: string): void {
    const url = `${API_BASE_URL}/api/v1/ideas/${ideaId}/export/markdown`;
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute(
      "download",
      `${title.toLowerCase().replace(/ /g, "-")}-blueprint.md`
    );
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  },
};
