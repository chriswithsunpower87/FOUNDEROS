/**
 * File: src/components/workspace/ShareButton.tsx
 * Purpose: Share a completed blueprint via a public link.
 * Responsibilities:
 *   - Toggle the idea's is_public flag via POST /ideas/{id}/toggle-public
 *   - Copy the public blueprint URL to clipboard when made public
 *   - Show current share state (public / private) with appropriate UI
 * Dependencies:
 *   - hooks/useIdeas (useTogglePublic)
 *   - lib/constants (API_BASE_URL)
 */

"use client";

import { useState } from "react";
import { Globe, Lock, Copy, Check } from "lucide-react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ideaService } from "@/services/ideaService";

interface ShareButtonProps {
  ideaId: string;
  isPublic: boolean;
}

/**
 * ShareButton
 * Description: Lets the owner toggle a blueprint between public and private.
 *   When made public, the shareable URL is copied to clipboard automatically.
 */
export function ShareButton({ ideaId, isPublic }: ShareButtonProps) {
  const [copied, setCopied] = useState(false);
  const queryClient = useQueryClient();

  const { mutate: togglePublic, isPending } = useMutation({
    /**
     * Purpose: Call the toggle-public API endpoint.
     * Returns: Updated Idea with new is_public value.
     */
    mutationFn: () => ideaService.togglePublic(ideaId),
    onSuccess: (updatedIdea) => {
      // Refresh the idea cache so is_public reflects immediately
      queryClient.setQueryData(["idea", ideaId], updatedIdea);
      queryClient.invalidateQueries({ queryKey: ["ideas"] });

      // Auto-copy the public URL to clipboard when going public
      if (updatedIdea.is_public) {
        const publicUrl = `${window.location.origin}/blueprint/${ideaId}`;
        navigator.clipboard.writeText(publicUrl).then(() => {
          setCopied(true);
          setTimeout(() => setCopied(false), 3000);
        });
      }
    },
  });

  const publicUrl = `${typeof window !== "undefined" ? window.location.origin : ""}/blueprint/${ideaId}`;

  if (isPublic) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Globe className="w-4 h-4 text-blue-500" />
            <div>
              <p className="text-sm font-medium text-blue-800">Blueprint is public</p>
              <p className="text-xs text-blue-600">Anyone with the link can view it</p>
            </div>
          </div>
          <button
            onClick={() => togglePublic()}
            disabled={isPending}
            className="flex items-center gap-1.5 text-xs text-blue-600 hover:text-blue-800 border border-blue-300 hover:border-blue-400 px-2.5 py-1.5 rounded-lg transition-colors"
          >
            <Lock className="w-3 h-3" />
            Make Private
          </button>
        </div>

        {/* Shareable URL row */}
        <div className="flex items-center gap-2 bg-white border border-blue-200 rounded-lg px-3 py-2">
          <span className="text-xs text-slate-500 truncate flex-1 font-mono">
            {publicUrl}
          </span>
          <button
            onClick={() => {
              navigator.clipboard.writeText(publicUrl).then(() => {
                setCopied(true);
                setTimeout(() => setCopied(false), 3000);
              });
            }}
            className="flex items-center gap-1 text-xs font-medium text-blue-600 hover:text-blue-800 flex-shrink-0 transition-colors"
          >
            {copied ? (
              <>
                <Check className="w-3 h-3 text-green-500" />
                <span className="text-green-600">Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-3 h-3" />
                Copy
              </>
            )}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-between bg-slate-50 border border-slate-200 rounded-xl p-4">
      <div className="flex items-center gap-2">
        <Lock className="w-4 h-4 text-slate-400" />
        <div>
          <p className="text-sm font-medium text-slate-700">Blueprint is private</p>
          <p className="text-xs text-slate-500">Only you can view it</p>
        </div>
      </div>
      <button
        onClick={() => togglePublic()}
        disabled={isPending}
        className="flex items-center gap-1.5 bg-blue-500 hover:bg-blue-600 disabled:opacity-50 text-white text-xs font-medium px-3 py-1.5 rounded-lg transition-colors"
      >
        <Globe className="w-3 h-3" />
        {isPending ? "Sharing…" : "Share Blueprint"}
      </button>
    </div>
  );
}
