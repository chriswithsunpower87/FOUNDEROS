/**
 * File: src/app/providers.tsx
 * Purpose: React context providers wrapper.
 * Responsibilities:
 *   - Wrap children with QueryClientProvider (React Query)
 *   - Restore user session from localStorage token on every page load
 *     so "Welcome back, [name]" shows correctly after a refresh
 */

"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { authService } from "@/services/authService";
import { useAuthStore } from "@/store/authStore";

/**
 * SessionRestorer — invisible component that runs once on mount.
 * If a JWT exists in localStorage, it fetches /auth/me and populates
 * the Zustand auth store so the user's name appears immediately.
 */
function SessionRestorer() {
  const { setAuth, clearAuth } = useAuthStore();

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    authService
      .getMe()
      .then((user) => setAuth(user, token))
      .catch((err) => {
        // Only clear the token if the server explicitly rejected it (401 Unauthorized).
        // Do NOT clear on network errors or 5xx — those are transient failures
        // (e.g. backend restarting) and the token is still valid.
        if (err?.response?.status === 401) {
          clearAuth();
        }
      });
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return null;
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            retry: 1,
            staleTime: 30_000,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <SessionRestorer />
      {children}
    </QueryClientProvider>
  );
}
