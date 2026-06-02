/**
 * File: src/services/ideaService.ts
 * Purpose: API calls for idea CRUD and pipeline trigger endpoints.
 */

import api from "./api";
import type { CreateIdeaPayload, Idea, UpdateIdeaPayload } from "@/types/idea.types";
import type { APIResponse, PaginatedResponse } from "@/types/api.types";

export const ideaService = {
  /**
   * Create a new startup idea.
   * @param payload - Title, problem statement, target audience
   */
  async createIdea(payload: CreateIdeaPayload): Promise<Idea> {
    const response = await api.post<APIResponse<Idea>>("/ideas", payload);
    return response.data.data;
  },

  /**
   * List all ideas for the current user.
   * @param page - Page number (default 1)
   * @param pageSize - Items per page (default 20)
   */
  async listIdeas(
    page = 1,
    pageSize = 20
  ): Promise<PaginatedResponse<Idea>> {
    const response = await api.get<APIResponse<PaginatedResponse<Idea>>>(
      `/ideas?page=${page}&page_size=${pageSize}`
    );
    return response.data.data;
  },

  /**
   * Get a single idea by ID.
   * @param ideaId - UUID of the idea
   */
  async getIdea(ideaId: string): Promise<Idea> {
    const response = await api.get<APIResponse<Idea>>(`/ideas/${ideaId}`);
    return response.data.data;
  },

  /**
   * Update an idea's metadata (only when status is DRAFT).
   * @param ideaId - UUID of the idea
   * @param payload - Fields to update (all optional)
   */
  async updateIdea(ideaId: string, payload: UpdateIdeaPayload): Promise<Idea> {
    const response = await api.put<APIResponse<Idea>>(
      `/ideas/${ideaId}`,
      payload
    );
    return response.data.data;
  },

  /**
   * Delete an idea and all its reports.
   * @param ideaId - UUID of the idea
   */
  async deleteIdea(ideaId: string): Promise<void> {
    await api.delete(`/ideas/${ideaId}`);
  },

  /**
   * Trigger the 10-agent AI analysis pipeline.
   * @param ideaId - UUID of the idea to analyze
   */
  async analyzeIdea(ideaId: string): Promise<void> {
    await api.post(`/ideas/${ideaId}/analyze`);
  },
};
