/**
 * File: src/lib/utils.ts
 * Purpose: Shared utility functions used across the frontend.
 * Responsibilities:
 *   - cn() — merge Tailwind classes with clsx + tailwind-merge
 *   - formatDate() — human-readable date formatting
 *   - truncate() — truncate long strings
 */

import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merge Tailwind CSS class names, resolving conflicts.
 * Standard utility required by ShadCN UI components.
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/**
 * Format a date string or Date object to a readable format.
 * @param date - ISO string or Date object
 * @returns Human-readable date string (e.g. "June 2, 2026")
 */
export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(new Date(date));
}

/**
 * Truncate a string to a maximum length with ellipsis.
 * @param text - The string to truncate
 * @param maxLength - Maximum character length (default 100)
 * @returns Truncated string with "..." appended if needed
 */
export function truncate(text: string, maxLength: number = 100): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength).trimEnd() + "...";
}
