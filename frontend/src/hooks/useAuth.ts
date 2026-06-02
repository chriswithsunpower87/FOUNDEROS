/**
 * File: src/hooks/useAuth.ts
 * Purpose: Hook for authentication actions (login, register, logout).
 * Responsibilities:
 *   - Wrap authService calls with loading and error state
 *   - Update Zustand auth store after success
 *   - Redirect after login/register/logout
 */

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { authService } from "@/services/authService";
import { useAuthStore } from "@/store/authStore";
import type { LoginPayload, RegisterPayload } from "@/types/auth.types";

export function useAuth() {
  const router = useRouter();
  const { setAuth, clearAuth } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Register a new user and redirect to dashboard.
   * @param payload - Registration data
   */
  async function register(payload: RegisterPayload): Promise<void> {
    setIsLoading(true);
    setError(null);
    try {
      const { user, access_token } = await authService.register(payload);
      setAuth(user, access_token);
      router.push("/dashboard");
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail ?? "Registration failed. Please try again.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }

  /**
   * Login and redirect to dashboard.
   * @param payload - Login credentials
   */
  async function login(payload: LoginPayload): Promise<void> {
    setIsLoading(true);
    setError(null);
    try {
      const { user, access_token } = await authService.login(payload);
      setAuth(user, access_token);
      router.push("/dashboard");
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail ?? "Invalid email or password.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }

  /**
   * Logout and redirect to login page.
   */
  function logout(): void {
    clearAuth();
    router.push("/login");
  }

  return { register, login, logout, isLoading, error };
}
