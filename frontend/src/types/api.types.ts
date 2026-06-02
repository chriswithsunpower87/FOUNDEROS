/**
 * File: src/types/api.types.ts
 * Purpose: Generic API response wrapper types.
 */

export interface APIResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface APIError {
  success: false;
  error: {
    code: string;
    message: string;
    details: Record<string, unknown>;
  };
}
