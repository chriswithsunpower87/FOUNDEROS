/**
 * File: src/components/shared/AuthGuard.tsx
 * Purpose: Client-side route protection for authenticated pages.
 * Responsibilities:
 *   - Check for a JWT in localStorage on every render
 *   - Redirect to /login immediately if no token is found
 *   - Render a loading spinner while the session is being restored
 *     (token present but Zustand store not yet hydrated via /auth/me)
 * Dependencies:
 *   - next/navigation (useRouter)
 *   - store/authStore (useAuthStore)
 */

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface AuthGuardProps {
  children: React.ReactNode;
}

/**
 * AuthGuard
 * Description: Wraps any page tree that requires authentication.
 * Responsibilities:
 *   - Perform a synchronous localStorage check on mount (no API call)
 *   - Redirect unauthenticated users to /login without rendering children
 *   - Show a minimal loading spinner for the brief window between mount
 *     and the SessionRestorer in providers.tsx finishing /auth/me
 */
export function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter();
  /**
   * `checked` — becomes true once we have confirmed the token status.
   * Prevents a flash of the protected content before the redirect fires.
   */
  const [checked, setChecked] = useState(false);
  const [hasToken, setHasToken] = useState(false);

  useEffect(() => {
    /**
     * Purpose: Read the token synchronously from localStorage.
     *   This runs only on the client (useEffect) so no SSR issues.
     */
    const token = localStorage.getItem("access_token");

    if (!token) {
      // No token — redirect immediately, never render children
      router.replace("/login");
    } else {
      setHasToken(true);
    }

    setChecked(true);
  }, [router]);

  // While checking (< 1 frame on fast machines), render nothing
  if (!checked) return null;

  // No token — blank screen while the redirect fires
  if (!hasToken) return null;

  // Token exists — render the protected content
  return <>{children}</>;
}
