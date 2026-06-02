/**
 * File: src/components/workspace/ExportButtons.tsx
 * Purpose: Export buttons for PDF and Markdown blueprint download.
 */

"use client";

import { FileText, FileDown } from "lucide-react";
import { reportService } from "@/services/reportService";

interface ExportButtonsProps {
  ideaId: string;
  ideaTitle: string;
}

export function ExportButtons({ ideaId, ideaTitle }: ExportButtonsProps) {
  return (
    <div className="flex items-center gap-3 bg-green-50 border border-green-200 rounded-xl p-4">
      <div className="flex-1">
        <p className="text-sm font-medium text-green-800">Blueprint ready!</p>
        <p className="text-xs text-green-600">
          All 10 agents have completed — download your startup blueprint
        </p>
      </div>
      <div className="flex gap-2">
        <button
          onClick={() => reportService.downloadMarkdown(ideaId, ideaTitle)}
          className="flex items-center gap-1.5 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
        >
          <FileText className="w-3.5 h-3.5" />
          Markdown
        </button>
        <button
          onClick={() => reportService.downloadPDF(ideaId, ideaTitle)}
          className="flex items-center gap-1.5 bg-blue-500 hover:bg-blue-600 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
        >
          <FileDown className="w-3.5 h-3.5" />
          PDF
        </button>
      </div>
    </div>
  );
}
