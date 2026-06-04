/**
 * File: src/types/idea.types.ts
 * Purpose: TypeScript types for startup idea data structures.
 */

export type IdeaStatus = "DRAFT" | "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";

export interface Idea {
  id: string;
  user_id: string;
  title: string;
  problem_statement: string;
  target_audience: string;
  status: IdeaStatus;
  is_public: boolean;
  analysis_count: number;   // How many times analyzed — drives version picker
  created_at: string;
  updated_at: string;
}

export interface CreateIdeaPayload {
  title: string;
  problem_statement: string;
  target_audience: string;
}

export interface UpdateIdeaPayload {
  title?: string;
  problem_statement?: string;
  target_audience?: string;
}
