/**
 * File: src/app/(auth)/layout.tsx
 * Purpose: Shared layout for authentication pages (login, register).
 * Responsibilities:
 *   - Center content vertically and horizontally
 *   - Show FounderOS branding above the auth card
 */

import Link from "next/link";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-4">
      <Link
        href="/"
        className="text-2xl font-bold text-slate-900 mb-8 tracking-tight"
      >
        Founder<span className="text-blue-500">OS</span>
      </Link>
      <div className="w-full max-w-md">{children}</div>
    </div>
  );
}
