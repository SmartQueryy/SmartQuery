/**
 * Login Button Component
 * 
 * Google OAuth login button that handles authentication flow.
 * Redirects to backend OAuth endpoint and handles success/failure.
 */

'use client';

import React, { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from './AuthProvider';
import { api } from '@/lib/api';

interface LoginButtonProps {
  className?: string;
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  children?: React.ReactNode;
  redirectTo?: string;
  showIcon?: boolean;
}

export function LoginButton({
  className = '',
  variant = 'primary',
  size = 'md',
  children,
  redirectTo = '/dashboard',
  showIcon = true,
}: LoginButtonProps) {
  const { login, setError } = useAuth();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const searchParams = useSearchParams();

  // Check for error from OAuth callback
  const error = searchParams.get('error');
  const code = searchParams.get('code');

  /**
   * Handle OAuth callback
   */
  React.useEffect(() => {
    if (code && !isLoading) {
      handleOAuthCallback(code);
    }
  }, [code]);

  /**
   * Handle OAuth error
   */
  React.useEffect(() => {
    if (error) {
      setError(`Login failed: ${error}`);
    }
  }, [error, setError]);

  /**
   * Handle OAuth callback with authorization code
   */
  const handleOAuthCallback = async (authCode: string) => {
    try {
      setIsLoading(true);
      setError(null);

      // Exchange authorization code for tokens
      const response = await api.auth.googleLogin({
        google_token: authCode,
      });

      if (response.success && response.data) {
        // Login successful, handle tokens and user data
        const { user, access_token, refresh_token, expires_in } = response.data;
        
        // Login user with tokens
        login(user, {
          accessToken: access_token,
          refreshToken: refresh_token,
          expiresAt: Date.now() + expires_in * 1000,
        });

        // Redirect to dashboard or specified page
        router.push(redirectTo);
      } else {
        throw new Error('Login failed');
      }
    } catch (error) {
      console.error('OAuth callback failed:', error);
      setError('Failed to complete login. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handle login button click
   */
  const handleLoginClick = () => {
    try {
      setIsLoading(true);
      setError(null);

      // Redirect to backend OAuth endpoint
      const oauthUrl = `${process.env.NEXT_PUBLIC_API_URL}/auth/google`;
      window.location.href = oauthUrl;
    } catch (error) {
      console.error('Login redirect failed:', error);
      setError('Failed to start login process');
      setIsLoading(false);
    }
  };

  /**
   * Generate button classes
   */
  const getButtonClasses = () => {
    const baseClasses = 'btn font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2';
    
    const variantClasses = {
      primary: 'btn-primary bg-blue-600 hover:bg-blue-700 focus:ring-blue-500',
      secondary: 'btn-secondary bg-gray-600 hover:bg-gray-700 focus:ring-gray-500',
      outline: 'btn-outline border-2 border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white focus:ring-blue-500',
    };

    const sizeClasses = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2 text-base',
      lg: 'px-6 py-3 text-lg',
    };

    return `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`;
  };

  return (
    <button
      type="button"
      onClick={handleLoginClick}
      disabled={isLoading}
      className={getButtonClasses()}
    >
      {isLoading ? (
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          <span>Signing in...</span>
        </div>
      ) : (
        <div className="flex items-center space-x-2">
          {showIcon && (
            <svg
              className="w-5 h-5"
              viewBox="0 0 24 24"
              fill="currentColor"
            >
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
            </svg>
          )}
          <span>{children || 'Sign in with Google'}</span>
        </div>
      )}
    </button>
  );
}

/**
 * Alternative login button for different styling
 */
export function GoogleLoginButton(props: LoginButtonProps) {
  return (
    <LoginButton
      {...props}
      className="w-full max-w-sm mx-auto bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 focus:ring-blue-500"
      showIcon={false}
    >
      <div className="flex items-center justify-center space-x-3">
        <svg
          className="w-5 h-5"
          viewBox="0 0 24 24"
          fill="currentColor"
        >
          <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
          <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
          <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
          <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
        </svg>
        <span>Continue with Google</span>
      </div>
    </LoginButton>
  );
} 