/**
 * File: src/app/(auth)/register/page.tsx
 * Purpose: Registration page — renders the register form.
 */

import { RegisterForm } from "@/components/auth/RegisterForm";
import Link from "next/link";

export default function RegisterPage() {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Create your account</h1>
        <p className="text-slate-500 text-sm mt-1">
          Start building your startup blueprint for free
        </p>
      </div>
      <RegisterForm />
      <p className="text-center text-sm text-slate-500 mt-6">
        Already have an account?{" "}
        <Link
          href="/login"
          className="text-blue-500 hover:text-blue-600 font-medium"
        >
          Sign in
        </Link>
      </p>
    </div>
  );
}
