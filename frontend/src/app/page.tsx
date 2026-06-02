/**
 * File: src/app/page.tsx
 * Purpose: Landing page — the public homepage of FounderOS.
 */

import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 flex flex-col">
      {/* Navigation */}
      <nav className="flex items-center justify-between px-8 py-6 max-w-6xl mx-auto w-full">
        <div className="text-white font-bold text-2xl tracking-tight">
          Founder<span className="text-blue-400">OS</span>
        </div>
        <div className="flex items-center gap-4">
          <Link
            href="/login"
            className="text-slate-300 hover:text-white transition-colors text-sm font-medium"
          >
            Log In
          </Link>
          <Link
            href="/register"
            className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            Get Started Free
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <main className="flex-1 flex flex-col items-center justify-center text-center px-6 py-20 max-w-4xl mx-auto">
        <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-medium px-3 py-1 rounded-full mb-8">
          Powered by 10 AI Specialist Agents
        </div>

        <h1 className="text-5xl md:text-7xl font-bold text-white leading-tight mb-6">
          From Startup Idea to{" "}
          <span className="text-blue-400">Execution Blueprint</span>
        </h1>

        <p className="text-xl text-slate-400 max-w-2xl mb-12 leading-relaxed">
          Enter your startup idea. Our AI agents — market researcher, product
          manager, architect, and 7 more specialists — generate a complete
          startup blueprint in minutes.
        </p>

        <Link
          href="/register"
          className="bg-blue-500 hover:bg-blue-600 text-white px-8 py-4 rounded-xl text-lg font-semibold transition-colors shadow-lg shadow-blue-500/25"
        >
          Build Your Blueprint →
        </Link>

        {/* Feature grid */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-20 w-full max-w-3xl">
          {[
            "Market Research",
            "Competitor Analysis",
            "PRD Generation",
            "System Architecture",
            "Database Design",
            "API Design",
            "UI/UX Planning",
            "MVP Roadmap",
            "GTM Strategy",
            "Risk Analysis",
          ].map((feature) => (
            <div
              key={feature}
              className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-3 text-slate-400 text-xs text-center"
            >
              {feature}
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
