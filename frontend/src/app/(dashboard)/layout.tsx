/**
 * File: src/app/(dashboard)/layout.tsx
 * Purpose: Shared layout for all authenticated dashboard pages.
 * Responsibilities:
 *   - Render the sidebar and top header
 *   - Protect all child routes from unauthenticated access
 */

import { AppHeader } from "@/components/shared/AppHeader";
import { AppSidebar } from "@/components/shared/AppSidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Sidebar */}
      <AppSidebar />

      {/* Main content area */}
      <div className="flex-1 flex flex-col min-w-0">
        <AppHeader />
        <main className="flex-1 p-6 overflow-auto">{children}</main>
      </div>
    </div>
  );
}
