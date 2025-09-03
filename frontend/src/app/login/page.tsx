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
import { useAuth } from '@/components/auth/AuthProvider';
import { LoginForm } from '@/components/auth/LoginForm';
import { FeaturesPreview } from '@/components/auth/FeaturesPreview';
import { ErrorDisplay } from '@/components/auth/ErrorDisplay';

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
    <div className="min-h-screen w-full flex items-center justify-center bg-background p-6 md:p-10">
      <div className="w-full max-w-sm mx-auto flex flex-col items-center gap-6">
        {/* Logo + SmartQuery */}
        <div className="flex flex-col items-center gap-3">
          <Image src="/smartquery-logo.svg" alt="SmartQuery Logo" width={64} height={64} className="w-16 h-16" />
          <h1 className="text-3xl font-bold text-foreground tracking-tight">SmartQuery</h1>
        </div>
        
        {/* Error Display */}
        {error && <ErrorDisplay error={error} />}
        
        {/* Login Form */}
        <LoginForm onDevLogin={handleDevLogin} />
        
        {/* Features Preview */}
        <FeaturesPreview />
        
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