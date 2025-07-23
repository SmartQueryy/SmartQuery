/**
 * Login Page
 * 
 * Login page with Google OAuth integration.
 * Handles OAuth callback and error display.
 */

"use client";

import React, { useEffect, Suspense } from "react";
import Image from "next/image.js";
import { useRouter, useSearchParams } from "next/navigation.js";
import { GoogleLoginButton } from '@/components/auth/LoginButton';
import { useAuth } from '@/components/auth/AuthProvider';
import { CloudArrowUpIcon, ChatBubbleLeftRightIcon, MagnifyingGlassIcon, ChartBarIcon, ShieldCheckIcon, TableCellsIcon } from "@heroicons/react/24/outline";

const FEATURES = [
  { label: "Upload CSVs Instantly", icon: <CloudArrowUpIcon className="h-6 w-6 text-indigo-600 dark:text-indigo-400" /> },
  { label: "Ask Data Questions", icon: <ChatBubbleLeftRightIcon className="h-6 w-6 text-indigo-600 dark:text-indigo-400" /> },
  { label: "AI-Powered Insights", icon: <MagnifyingGlassIcon className="h-6 w-6 text-indigo-600 dark:text-indigo-400" /> },
  { label: "Visualize Results", icon: <ChartBarIcon className="h-6 w-6 text-indigo-600 dark:text-indigo-400" /> },
  { label: "Secure & Private", icon: <ShieldCheckIcon className="h-6 w-6 text-indigo-600 dark:text-indigo-400" /> },
  { label: "No SQL Needed", icon: <TableCellsIcon className="h-6 w-6 text-indigo-600 dark:text-indigo-400" /> },
];

function LoginPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated, error, setError, login } = useAuth();
  const oauthError = searchParams.get('error');

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  useEffect(() => {
    if (oauthError) {
      setError(`Login failed: ${oauthError}`);
    }
  }, [oauthError, setError]);

  useEffect(() => {
    return () => { setError(null); };
  }, [setError]);

  // Dev login handler for bypass/testing
  const handleDevLogin = () => {
    // Mock user data for dev login
    login({
      id: 'dev-user',
      email: 'dev@smartquery.ai',
      name: 'Dev User',
      avatar_url: '',
      created_at: new Date().toISOString(),
    }, {
      accessToken: 'dev-access-token',
      refreshToken: 'dev-refresh-token',
      expiresAt: Date.now() + 3600 * 1000,
    });
    router.push('/dashboard');
  };

  return (
    <div className="fixed inset-0 min-h-screen w-full flex items-center justify-center bg-gradient-to-br from-indigo-100 via-indigo-200 to-indigo-300 dark:from-gray-900 dark:via-indigo-950 dark:to-indigo-900 overflow-hidden select-none">
      <div className="w-full max-w-md mx-auto flex flex-col items-center gap-8 p-6">
        {/* Logo + SmartQuery */}
        <div className="flex flex-col items-center gap-2">
          <Image src="/smartquery-logo.svg" alt="SmartQuery Logo" width={64} height={64} className="w-16 h-16" />
          <span className="text-3xl md:text-4xl font-bold text-indigo-700 dark:text-indigo-400 tracking-tight">SmartQuery</span>
        </div>
        {/* Welcome Text */}
        <div className="text-center">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white mb-2">Welcome to SmartQuery</h2>
          <p className="text-base md:text-lg text-gray-700 dark:text-gray-200">Sign in to access your data analysis dashboard</p>
        </div>
        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 w-full">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Authentication Error</h3>
                <div className="mt-2 text-sm text-red-700">
                  <p>{error}</p>
                </div>
              </div>
            </div>
          </div>
        )}
        {/* Login Card */}
        <div className="w-full bg-white dark:bg-gray-950 py-8 px-6 shadow-xl rounded-2xl flex flex-col gap-6">
          <GoogleLoginButton size="lg" redirectTo="/dashboard" className="w-full" showIcon={true} />
          {/* Dev Login Button for testing */}
          <button
            onClick={handleDevLogin}
            className="w-full mt-2 py-3 rounded-xl bg-indigo-200 dark:bg-indigo-700 text-indigo-900 dark:text-white font-semibold text-base hover:bg-indigo-300 dark:hover:bg-indigo-600 transition-colors"
            type="button"
          >
            Dev Login (Bypass)
          </button>
        </div>
        {/* Features Preview */}
        <div className="w-full bg-white dark:bg-gray-950 rounded-2xl p-6 shadow flex flex-col gap-4">
          <h3 className="text-lg font-semibold text-indigo-700 dark:text-indigo-200 mb-2">What you can do with SmartQuery</h3>
          <ul className="grid grid-cols-1 gap-2 md:grid-cols-2">
            {FEATURES.map((f) => (
              <li key={f.label} className="flex items-center gap-3 text-base font-medium text-indigo-700 dark:text-indigo-300 tracking-wide">
                {f.icon}
                {f.label}
              </li>
            ))}
          </ul>
        </div>
        {/* Footer */}
        <div className="text-center w-full">
          <p className="text-xs text-gray-500 dark:text-gray-400">
            By signing in, you agree to our{' '}
            <a href="/terms-of-service" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-500 underline">Terms of Service</a>{' '}and{' '}
            <a href="/privacy-policy" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-500 underline">Privacy Policy</a>
          </p>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    }>
      <LoginPageContent />
    </Suspense>
  );
} 