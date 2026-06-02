/**
 * File: src/services/authService.ts
 * Purpose: API calls for authentication endpoints.
 * Responsibilities:
 *   - login(), register(), getMe()
 *   - Store/clear JWT in localStorage
 */

import api from "./api";
import type { AuthResponse, LoginPayload, RegisterPayload, User } from "@/types/auth.types";
import type { APIResponse } from "@/types/api.types";

export const authService = {
  /**
   * Register a new user account.
   * @param payload - Registration data (name, email, password)
   * @returns AuthResponse with JWT and user profile
   */
  async register(payload: RegisterPayload): Promise<AuthResponse> {
    const response = await api.post<APIResponse<AuthResponse>>(
      "/auth/register",
      payload
    );
    const { access_token, user } = response.data.data;
    localStorage.setItem("access_token", access_token);
    return response.data.data;
  },

  /**
   * Login with email and password.
   * @param payload - Login credentials
   * @returns AuthResponse with JWT and user profile
   */
  async login(payload: LoginPayload): Promise<AuthResponse> {
    const response = await api.post<APIResponse<AuthResponse>>(
      "/auth/login",
      payload
    );
    const { access_token } = response.data.data;
    localStorage.setItem("access_token", access_token);
    return response.data.data;
  },

  /**
   * Get the currently authenticated user's profile.
   * @returns User profile
   */
  async getMe(): Promise<User> {
    const response = await api.get<APIResponse<User>>("/auth/me");
    return response.data.data;
  },

  /**
   * Clear the stored token (logout).
   */
  logout(): void {
    localStorage.removeItem("access_token");
  },
};
