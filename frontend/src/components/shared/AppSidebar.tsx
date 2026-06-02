/**
 * File: src/components/shared/AppSidebar.tsx
 * Purpose: Left navigation sidebar for authenticated pages.
 */

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Lightbulb } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
];

export function AppSidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-56 bg-white border-r border-slate-200 flex flex-col flex-shrink-0">
      {/* Logo */}
      <div className="h-14 flex items-center px-5 border-b border-slate-200">
        <span className="text-xl font-bold text-slate-900 tracking-tight">
          Founder<span className="text-blue-500">OS</span>
        </span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
              pathname === href || pathname.startsWith(href + "/")
                ? "bg-blue-50 text-blue-600"
                : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
            )}
          >
            <Icon className="w-4 h-4" />
            {label}
          </Link>
        ))}
      </nav>

      {/* Bottom branding */}
      <div className="p-4 border-t border-slate-200">
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <Lightbulb className="w-3 h-3" />
          AI-powered startup blueprints
        </div>
      </div>
    </aside>
  );
}
