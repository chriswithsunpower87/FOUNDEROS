/**
 * File: src/components/shared/AppHeader.tsx
 * Purpose: Top navigation bar for authenticated dashboard pages.
 */

"use client";

import { LogOut, User } from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import { useAuth } from "@/hooks/useAuth";

export function AppHeader() {
  const { user } = useAuthStore();
  const { logout } = useAuth();

  return (
    <header className="h-14 border-b border-slate-200 bg-white flex items-center justify-between px-6 flex-shrink-0">
      <div className="text-sm text-slate-500">
        Welcome back, <span className="font-medium text-slate-900">{user?.name}</span>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-sm text-slate-600">
          <User className="w-4 h-4" />
          <span>{user?.email}</span>
        </div>
        <button
          onClick={logout}
          className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-red-500 transition-colors"
        >
          <LogOut className="w-4 h-4" />
          Logout
        </button>
      </div>
    </header>
  );
}
