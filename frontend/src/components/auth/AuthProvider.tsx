/**
 * Authentication Provider
 * 
 * React Context provider for authentication state management.
 * Provides authentication context to the entire application.
 */

'use client';

import React, { createContext, useContext, useEffect, ReactNode } from 'react';
import { useAuthStore } from '@/lib/store/auth';
import { refreshToken, logout as authLogout } from '@/lib/auth';
import { api, apiClient } from '@/lib/api';
import type { User } from '@/lib/types';

interface AuthContextType {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (user: User, tokens: { accessToken: string; refreshToken: string; expiresAt: number }) => void;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  setError: (error: string | null) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const {
    user,
    accessToken,
    isAuthenticated,
    isLoading,
    error,
    setTokens,
    setUser,
    clearTokens,
    clearUser,
    setLoading,
    setError,
    loadSession,
  } = useAuthStore();

  /**
   * Initialize authentication state on mount
   */
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        setLoading(true);
        
        // Load session from localStorage
        loadSession();
        
        // Set initial token in API client
        const currentToken = accessToken || localStorage.getItem('access_token');
        if (currentToken) {
          apiClient.setAccessToken(currentToken);
        }
        
        // If we have tokens, verify them with the server
        if (isAuthenticated && accessToken) {
          try {
            // Verify token by calling /auth/me endpoint
            const response = await api.auth.getCurrentUser();
            
            if (response.success && response.data) {
              // Token is valid, update user info
              setUser(response.data);
            } else {
              // Token is invalid, clear session
              await handleLogout();
            }
          } catch (error) {
            console.error('Token verification failed:', error);
            // Token verification failed, clear session
            await handleLogout();
          }
        }
      } catch (error) {
        console.error('Auth initialization failed:', error);
        setError('Failed to initialize authentication');
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []); // Only run on mount

  /**
   * Handle login with user data and tokens
   */
  const handleLogin = (user: User, tokens: { accessToken: string; refreshToken: string; expiresAt: number }) => {
    try {
      setUser(user);
      setTokens(tokens.accessToken, tokens.refreshToken, tokens.expiresAt - Date.now());
      apiClient.setAccessToken(tokens.accessToken);
      setError(null);
    } catch (error) {
      console.error('Login failed:', error);
      setError('Failed to complete login');
    }
  };

  /**
   * Handle logout
   */
  const handleLogout = async () => {
    try {
      setLoading(true);
      
      // Call server logout endpoint if we have a token
      if (accessToken) {
        try {
          await authLogout();
        } catch (error) {
          console.warn('Server logout failed:', error);
          // Continue with local logout even if server call fails
        }
      }
      
      // Clear local state
      clearTokens();
      clearUser();
      apiClient.setAccessToken(null);
      setError(null);
    } catch (error) {
      console.error('Logout failed:', error);
      setError('Failed to logout properly');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Refresh access token
   */
  const handleRefreshToken = async () => {
    try {
      setLoading(true);
      
      const tokens = await refreshToken();
      
      // Update tokens in store
      setTokens(tokens.accessToken, tokens.refreshToken, tokens.expiresAt - Date.now());
      apiClient.setAccessToken(tokens.accessToken);
      setError(null);
    } catch (error) {
      console.error('Token refresh failed:', error);
      setError('Failed to refresh authentication');
      
      // If refresh fails, logout the user
      await handleLogout();
    } finally {
      setLoading(false);
    }
  };

  /**
   * Context value
   */
  const contextValue: AuthContextType = {
    user,
    accessToken,
    isAuthenticated,
    isLoading,
    error,
    login: handleLogin,
    logout: handleLogout,
    refreshToken: handleRefreshToken,
    setError,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Hook to use authentication context
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}

/**
 * Hook to check if user is authenticated
 */
export function useIsAuthenticated(): boolean {
  const { isAuthenticated } = useAuth();
  return isAuthenticated;
}

/**
 * Hook to get current user
 */
export function useCurrentUser(): User | null {
  const { user } = useAuth();
  return user;
}

/**
 * Hook to get access token
 */
export function useAccessToken(): string | null {
  const { accessToken } = useAuth();
  return accessToken;
} 