/**
 * Authentication Store
 * 
 * Global state management for authentication using Zustand.
 * Handles user session, tokens, and authentication state persistence.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '../types';
import { TokenManager, UserManager } from '../auth';

interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
}

export interface AuthState {
  // State
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  setTokens: (accessToken: string, refreshToken: string, expiresIn: number) => void;
  setUser: (user: User) => void;
  clearTokens: () => void;
  clearUser: () => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  loadSession: () => void;
  logout: () => void;
}

/**
 * Create the authentication store with persistence
 */
export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: true,
      error: null,

      // Actions
      setTokens: (accessToken: string, refreshToken: string, expiresIn: number) => {
        // Store tokens in both Zustand state and localStorage
        TokenManager.setTokens(accessToken, refreshToken, expiresIn);
        
        set({
          accessToken,
          refreshToken,
          isAuthenticated: true,
          error: null,
        });
      },

      setUser: (user: User) => {
        // Store user in both Zustand state and localStorage
        UserManager.setUser(user);
        
        set({
          user,
          isAuthenticated: true,
          error: null,
        });
      },

      clearTokens: () => {
        // Clear tokens from both Zustand state and localStorage
        TokenManager.clearTokens();
        
        set({
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        });
      },

      clearUser: () => {
        // Clear user from both Zustand state and localStorage
        UserManager.clearUser();
        
        set({
          user: null,
          isAuthenticated: false,
        });
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },

      setError: (error: string | null) => {
        set({ error });
      },

      loadSession: () => {
        const { setLoading, setError } = get();
        
        try {
          setLoading(true);
          setError(null);

          // Check if we have valid tokens
          const hasValidTokens = TokenManager.hasValidTokens();
          
          if (hasValidTokens) {
            // Load tokens from localStorage
            const accessToken = TokenManager.getAccessToken();
            const refreshToken = TokenManager.getRefreshToken();
            
            // Load user from localStorage
            const user = UserManager.getUser();
            
            if (accessToken && refreshToken && user) {
              set({
                accessToken,
                refreshToken,
                user,
                isAuthenticated: true,
                isLoading: false,
                error: null,
              });
              return;
            }
          }

          // No valid session found
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        } catch (error) {
          console.error('Error loading session:', error);
          setError('Failed to load session');
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      },

      logout: () => {
        const { clearTokens, clearUser, setError } = get();
        
        try {
          // Clear all authentication data
          clearTokens();
          clearUser();
          setError(null);
          
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        } catch (error) {
          console.error('Error during logout:', error);
          setError('Failed to logout properly');
        }
      },
    }),
    {
      name: 'smartquery-auth', // localStorage key
      partialize: (state) => ({
        // Only persist these fields to localStorage
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

/**
 * Convenience hooks for common auth operations
 */
export const useAuth = () => {
  const store = useAuthStore();
  
  return {
    // State
    user: store.user,
    accessToken: store.accessToken,
    isAuthenticated: store.isAuthenticated,
    isLoading: store.isLoading,
    error: store.error,
    
    // Actions
    login: (user: User, tokens: AuthTokens) => {
      store.setUser(user);
      store.setTokens(tokens.accessToken, tokens.refreshToken, tokens.expiresAt - Date.now());
    },
    
    logout: store.logout,
    setLoading: store.setLoading,
    setError: store.setError,
    loadSession: store.loadSession,
  };
};

/**
 * Hook to check if user is authenticated
 */
export const useIsAuthenticated = () => {
  return useAuthStore((state) => state.isAuthenticated);
};

/**
 * Hook to get current user
 */
export const useCurrentUser = () => {
  return useAuthStore((state) => state.user);
};

/**
 * Hook to get access token
 */
export const useAccessToken = () => {
  return useAuthStore((state) => state.accessToken);
}; 