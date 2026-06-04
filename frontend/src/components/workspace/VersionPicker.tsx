/**
 * File: src/components/workspace/VersionPicker.tsx
 * Purpose: Lets users browse past analysis versions of their blueprint.
 * Responsibilities:
 *   - Show a version selector when analysis_count > 1
 *   - Highlight the currently viewed version
 *   - Label the latest version clearly
 * Dependencies:
 *   - types/idea.types (Idea)
 */

"use client";

import { History } from "lucide-react";
import { cn } from "@/lib/utils";

interface VersionPickerProps {
  versions: number[];
  selectedVersion: number;
  latestVersion: number;
  onSelect: (version: number) => void;
}

/**
 * VersionPicker
 * Description: Horizontal pill-style selector for browsing blueprint history.
 *   Only renders if there are 2+ versions (single-run ideas skip this UI).
 */
export function VersionPicker({
  versions,
  selectedVersion,
  latestVersion,
  onSelect,
}: VersionPickerProps) {
  if (versions.length <= 1) return null;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4">
      <div className="flex items-center gap-2 mb-3">
        <History className="w-4 h-4 text-slate-400" />
        <span className="text-sm font-medium text-slate-700">
          Analysis History
        </span>
        <span className="text-xs text-slate-400 ml-auto">
          {versions.length} runs — select a version to compare
        </span>
      </div>

      <div className="flex gap-2 flex-wrap">
        {versions.map((v) => {
          const isSelected = v === selectedVersion;
          const isLatest = v === latestVersion;

          return (
            <button
              key={v}
              onClick={() => onSelect(v)}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all border",
                isSelected
                  ? "bg-blue-500 text-white border-blue-500 shadow-sm"
                  : "bg-white text-slate-600 border-slate-200 hover:border-blue-300 hover:text-blue-600"
              )}
            >
              <span>v{v}</span>
              {isLatest && (
                <span
                  className={cn(
                    "text-xs px-1 rounded",
                    isSelected
                      ? "bg-blue-400 text-white"
                      : "bg-green-100 text-green-700"
                  )}
                >
                  latest
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
