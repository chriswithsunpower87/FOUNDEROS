/**
 * File: src/app/layout.tsx
 * Purpose: Root layout — wraps the entire application with providers.
 * Responsibilities:
 *   - Provide React Query client (TanStack Query)
 *   - Set global HTML metadata
 *   - Apply global CSS
 */

import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "FounderOS — From Startup Idea to Execution Blueprint",
  description:
    "AI-powered startup planning platform. Enter your idea, get a complete startup blueprint.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
