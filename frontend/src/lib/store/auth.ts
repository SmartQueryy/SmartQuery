/**
 * Authentication Store
 * 
 * Global state management for authentication using Zustand.
 * Handles user session, tokens, and authentication state persistence.
 */

import { create } from 'zustand';
import type { User } from '@/lib/types';
import { TokenManager, UserManager } from '@/lib/auth';

interface AuthState {
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
  setError: (error: string | null) => void;
  setLoading: (loading: boolean) => void;
  loadSession: () => void;
  logout: () => void;
  login: (user: User, tokens: { accessToken: string; refreshToken: string; expiresAt: number }) => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,

  setTokens: (accessToken, refreshToken, expiresIn) => {
    TokenManager.setTokens(accessToken, refreshToken, expiresIn);
    set({
      accessToken,
      refreshToken,
      isAuthenticated: true,
      error: null,
    });
  },

  setUser: (user) => {
    UserManager.setUser(user);
    set({
      user,
      isAuthenticated: true,
      error: null,
    });
  },

  clearTokens: () => {
    TokenManager.clearTokens();
    set({
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
    });
  },

  clearUser: () => {
    UserManager.clearUser();
    set({
      user: null,
      isAuthenticated: false,
    });
  },

  setError: (error) => {
    set({ error });
  },

  setLoading: (isLoading) => {
    set({ isLoading });
  },

  loadSession: () => {
    try {
      set({ isLoading: true });
      
      const accessToken = TokenManager.getAccessToken();
      const refreshToken = TokenManager.getRefreshToken();
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
      } else {
        set({
          accessToken: null,
          refreshToken: null,
          user: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
        });
      }
    } catch (error) {
      set({ 
        error: 'Failed to load session',
        isLoading: false 
      });
    }
  },

  logout: () => {
    try {
      TokenManager.clearTokens();
      UserManager.clearUser();
      set({
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        error: null,
      });
    } catch (error) {
      set({ error: 'Failed to logout properly' });
    }
  },

  login: (user: User, tokens: { accessToken: string; refreshToken: string; expiresAt: number }) => {
    try {
      TokenManager.setTokens(tokens.accessToken, tokens.refreshToken, tokens.expiresAt - Date.now());
      UserManager.setUser(user);
      set({
        user,
        accessToken: tokens.accessToken,
        refreshToken: tokens.refreshToken,
        isAuthenticated: true,
        error: null,
      });
    } catch (error) {
      set({ error: 'Failed to complete login' });
    }
  },
}));

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
    login: (user: User, tokens: { accessToken: string; refreshToken: string; expiresAt: number }) => {
      store.login(user, tokens);
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