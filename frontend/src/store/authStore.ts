/**
 * File: src/store/authStore.ts
 * Purpose: Zustand global store for authentication state.
 * Responsibilities:
 *   - Hold the current user and token
 *   - Expose login, logout, and setUser actions
 *   - Persist token to localStorage
 */

import { create } from "zustand";
import type { User } from "@/types/auth.types";

interface AuthState {
  /** Currently authenticated user, or null if not logged in */
  user: User | null;
  /** JWT access token, or null if not logged in */
  token: string | null;
  /** True if a user is authenticated */
  isAuthenticated: boolean;

  /** Set user and token after successful login/register */
  setAuth: (user: User, token: string) => void;
  /** Clear auth state (logout) */
  clearAuth: () => void;
  /** Update just the user object (e.g. after profile update) */
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,

  setAuth: (user, token) => {
    localStorage.setItem("access_token", token);
    set({ user, token, isAuthenticated: true });
  },

  clearAuth: () => {
    localStorage.removeItem("access_token");
    set({ user: null, token: null, isAuthenticated: false });
  },

  setUser: (user) => set({ user }),
}));
