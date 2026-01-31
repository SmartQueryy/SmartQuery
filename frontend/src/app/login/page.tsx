/**
 * Login Page
 *
 * Two-column layout: form left, value prop right.
 * Handles OAuth callback and error display.
 */

"use client";

import React, { useEffect, Suspense } from "react";
import Image from "next/image";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/components/auth/AuthProvider";
import { LoginForm } from "@/components/auth/LoginForm";
import { ErrorDisplay } from "@/components/auth/ErrorDisplay";
import {
  CloudUpload,
  MessageCircle,
  BarChart3,
  ShieldCheck,
  CheckCircle2,
} from "lucide-react";
import { cn } from "@/lib/utils";

const LOGIN_FEATURES = [
  { icon: CloudUpload, label: "Upload CSVs instantly" },
  { icon: MessageCircle, label: "Ask in plain English" },
  { icon: BarChart3, label: "Charts & insights" },
  { icon: ShieldCheck, label: "Secure & private" },
];

function LoginPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated, error, setError, login } = useAuth();
  const oauthError = searchParams.get("error");

  useEffect(() => {
    if (isAuthenticated) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, router]);

  useEffect(() => {
    if (oauthError) {
      setError(`Login failed: ${oauthError}`);
    }
  }, [oauthError, setError]);

  useEffect(() => {
    return () => {
      setError(null);
    };
  }, [setError]);

  const handleDevLogin = () => {
    login(
      {
        id: "dev-user",
        email: "dev@smartquery.ai",
        name: "Dev User",
        avatar_url: "",
        created_at: new Date().toISOString(),
      },
      {
        accessToken: "dev-access-token",
        refreshToken: "dev-refresh-token",
        expiresAt: Date.now() + 3600 * 1000,
      }
    );
    router.push("/dashboard");
  };

  return (
    <div className="min-h-screen w-full flex flex-col md:flex-row bg-white dark:bg-gray-900">
      {/* Left: Form */}
      <div className="flex-1 flex items-center justify-center p-6 md:p-10 lg:p-16 relative overflow-hidden">
        <div
          className="absolute inset-0 bg-gradient-to-br from-indigo-50/80 via-white to-indigo-50/50 dark:from-indigo-950/20 dark:via-gray-900 dark:to-indigo-950/20 pointer-events-none"
          aria-hidden
        />
        <div className="relative w-full max-w-sm flex flex-col items-center gap-6 animate-fade-up">
          <Link
            href="/"
            className="flex items-center gap-2 transition-opacity hover:opacity-90"
            aria-label="SmartQuery home"
          >
            <Image
              src="/smartquery-logo.svg"
              alt="SmartQuery"
              width={48}
              height={48}
              className="w-12 h-12"
            />
            <span className="text-2xl font-bold text-indigo-700 dark:text-indigo-400 tracking-tight">
              SmartQuery
            </span>
          </Link>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white text-center">
            Welcome back
          </h1>
          {error && <ErrorDisplay error={error} />}
          <LoginForm onDevLogin={handleDevLogin} />
          <p className="text-xs text-center text-gray-500 dark:text-gray-400">
            By signing in, you agree to our{" "}
            <Link href="/terms" className="text-indigo-600 dark:text-indigo-400 hover:underline">
              Terms of Service
            </Link>{" "}
            and{" "}
            <Link href="/privacy" className="text-indigo-600 dark:text-indigo-400 hover:underline">
              Privacy Policy
            </Link>
          </p>
        </div>
      </div>
      {/* Right: Value prop (desktop) */}
      <div className="hidden md:flex flex-1 flex-col justify-center bg-indigo-600 dark:bg-indigo-700 p-10 lg:p-16">
        <div className="max-w-md mx-auto space-y-8">
          <h2 className="text-2xl lg:text-3xl font-bold text-white">
            Query your data in plain English
          </h2>
          <p className="text-indigo-100 text-lg">
            Upload CSV files, ask questions naturally, and get instant answers and charts. No SQL required.
          </p>
          <ul className="space-y-4">
            {LOGIN_FEATURES.map((item, i) => {
              const Icon = item.icon;
              return (
                <li
                  key={item.label}
                  className="flex items-center gap-3 text-white"
                  style={{ animationDelay: `${i * 50}ms` }}
                >
                  <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-white/20">
                    <Icon className="h-5 w-5" aria-hidden />
                  </span>
                  <span className="font-medium">{item.label}</span>
                  <CheckCircle2 className="ml-auto h-5 w-5 text-indigo-200" aria-hidden />
                </li>
              );
            })}
          </ul>
          <p className="text-sm text-indigo-200">
            Join teams who use SmartQuery to get instant insights from their data.
          </p>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-white dark:bg-gray-900">
          <div className="flex flex-col items-center gap-4">
            <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" aria-hidden />
            <p className="text-gray-500 dark:text-gray-400">Loading...</p>
          </div>
        </div>
      }
    >
      <LoginPageContent />
    </Suspense>
  );
}
