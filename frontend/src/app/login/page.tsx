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
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const FEATURES = [
  { label: "Upload CSVs Instantly", icon: <CloudArrowUpIcon className="h-5 w-5 text-muted-foreground" /> },
  { label: "Ask Data Questions", icon: <ChatBubbleLeftRightIcon className="h-5 w-5 text-muted-foreground" /> },
  { label: "AI-Powered Insights", icon: <MagnifyingGlassIcon className="h-5 w-5 text-muted-foreground" /> },
  { label: "Visualize Results", icon: <ChartBarIcon className="h-5 w-5 text-muted-foreground" /> },
  { label: "Secure & Private", icon: <ShieldCheckIcon className="h-5 w-5 text-muted-foreground" /> },
  { label: "No SQL Needed", icon: <TableCellsIcon className="h-5 w-5 text-muted-foreground" /> },
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
    <div className="min-h-screen w-full flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-md mx-auto flex flex-col items-center gap-6">
        {/* Logo + SmartQuery */}
        <div className="flex flex-col items-center gap-3">
          <Image src="/smartquery-logo.svg" alt="SmartQuery Logo" width={64} height={64} className="w-16 h-16" />
          <h1 className="text-3xl font-bold text-foreground tracking-tight">SmartQuery</h1>
        </div>
        
        {/* Welcome Text */}
        <div className="text-center space-y-2">
          <h2 className="text-xl font-semibold text-foreground">Welcome back</h2>
          <p className="text-sm text-muted-foreground">Sign in to access your data analysis dashboard</p>
        </div>
        {/* Error Display */}
        {error && (
          <Card className="w-full border-destructive/50 bg-destructive/10">
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 mt-0.5">
                  <svg className="h-4 w-4 text-destructive" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-destructive mb-1">Authentication Error</h3>
                  <p className="text-sm text-destructive/80">{error}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
        {/* Login Card */}
        <Card className="w-full">
          <CardContent className="p-6 space-y-4">
            <GoogleLoginButton size="lg" redirectTo="/dashboard" className="w-full" showIcon={true} />
            {/* Dev Login Button for testing */}
            <Button 
              onClick={handleDevLogin}
              variant="secondary"
              className="w-full"
              type="button"
            >
              Dev Login (Bypass)
            </Button>
          </CardContent>
        </Card>
        {/* Features Preview */}
        <Card className="w-full">
          <CardHeader>
            <CardTitle className="text-base">What you can do with SmartQuery</CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
              {FEATURES.map((f) => (
                <div key={f.label} className="flex items-center gap-3 text-sm text-muted-foreground">
                  {f.icon}
                  <span>{f.label}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
        {/* Footer */}
        <div className="text-center w-full">
          <p className="text-xs text-muted-foreground">
            By signing in, you agree to our{' '}
            <a href="/terms-of-service" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">Terms of Service</a>{' '}and{' '}
            <a href="/privacy-policy" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">Privacy Policy</a>
          </p>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center space-y-4">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    }>
      <LoginPageContent />
    </Suspense>
  );
} 