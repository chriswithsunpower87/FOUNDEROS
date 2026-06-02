/**
 * File: src/app/(auth)/login/page.tsx
 * Purpose: Login page — renders the login form.
 */

import { LoginForm } from "@/components/auth/LoginForm";
import Link from "next/link";

export default function LoginPage() {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Welcome back</h1>
        <p className="text-slate-500 text-sm mt-1">
          Sign in to your FounderOS account
        </p>
      </div>
      <LoginForm />
      <p className="text-center text-sm text-slate-500 mt-6">
        Don&apos;t have an account?{" "}
        <Link
          href="/register"
          className="text-blue-500 hover:text-blue-600 font-medium"
        >
          Sign up free
        </Link>
      </p>
    </div>
  );
}
