/**
 * File: src/components/workspace/ExportButtons.tsx
 * Purpose: Export buttons for PDF and Markdown blueprint download.
 * Responsibilities:
 *   - Call async download helpers from reportService
 *   - Show loading state while file is being generated
 *   - Show error toast if download fails
 */

"use client";

import { useState } from "react";
import { FileText, FileDown, Loader2 } from "lucide-react";
import { reportService } from "@/services/reportService";

interface ExportButtonsProps {
  ideaId: string;
  ideaTitle: string;
}

export function ExportButtons({ ideaId, ideaTitle }: ExportButtonsProps) {
  const [loadingPDF, setLoadingPDF] = useState(false);
  const [loadingMD, setLoadingMD] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleDownloadPDF() {
    setLoadingPDF(true);
    setError(null);
    try {
      await reportService.downloadPDF(ideaId, ideaTitle);
    } catch {
      setError("PDF generation failed. Please try again.");
    } finally {
      setLoadingPDF(false);
    }
  }

  async function handleDownloadMarkdown() {
    setLoadingMD(true);
    setError(null);
    try {
      await reportService.downloadMarkdown(ideaId, ideaTitle);
    } catch {
      setError("Markdown export failed. Please try again.");
    } finally {
      setLoadingMD(false);
    }
  }

  return (
    <div className="bg-green-50 border border-green-200 rounded-xl p-4 space-y-2">
      <div className="flex items-center gap-3">
        <div className="flex-1">
          <p className="text-sm font-medium text-green-800">Blueprint ready!</p>
          <p className="text-xs text-green-600">
            All 10 agents completed — download your startup blueprint
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleDownloadMarkdown}
            disabled={loadingMD || loadingPDF}
            className="flex items-center gap-1.5 bg-white border border-slate-300 hover:bg-slate-50 disabled:opacity-50 text-slate-700 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
          >
            {loadingMD ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <FileText className="w-3.5 h-3.5" />
            )}
            Markdown
          </button>
          <button
            onClick={handleDownloadPDF}
            disabled={loadingPDF || loadingMD}
            className="flex items-center gap-1.5 bg-blue-500 hover:bg-blue-600 disabled:opacity-50 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
          >
            {loadingPDF ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <FileDown className="w-3.5 h-3.5" />
            )}
            PDF
          </button>
        </div>
      </div>
      {error && (
        <p className="text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
          {error}
        </p>
      )}
    </div>
  );
}
