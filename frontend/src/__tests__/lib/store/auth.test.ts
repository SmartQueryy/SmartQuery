/**
 * Auth Store Tests
 * 
 * Tests for the authentication store functionality.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useAuthStore } from '@/lib/store/auth';
import { TokenManager, UserManager } from '@/lib/auth';

// Mock the auth utilities
vi.mock('@/lib/auth', () => ({
  TokenManager: {
    getAccessToken: vi.fn(),
    getRefreshToken: vi.fn(),
    getTokenExpiry: vi.fn(),
    setTokens: vi.fn(),
    clearTokens: vi.fn(),
    isTokenExpired: vi.fn(),
  },
  UserManager: {
    getUser: vi.fn(),
    setUser: vi.fn(),
    clearUser: vi.fn(),
  },
}));

describe('Auth Store', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset store to initial state
    act(() => {
      useAuthStore.setState({
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      });
    });
  });

  describe('setTokens', () => {
    it('should set tokens and update authentication state', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setTokens('access-token', 'refresh-token', 3600);
      });

      expect(TokenManager.setTokens).toHaveBeenCalledWith('access-token', 'refresh-token', 3600);
      expect(result.current.accessToken).toBe('access-token');
      expect(result.current.refreshToken).toBe('refresh-token');
      expect(result.current.isAuthenticated).toBe(true);
    });
  });

  describe('setUser', () => {
    it('should set user and update authentication state', () => {
      const { result } = renderHook(() => useAuthStore());
      const mockUser = {
        id: 'test-user-123',
        name: 'Test User',
        email: 'test@example.com',
        avatar_url: '',
        created_at: '2024-01-01T00:00:00Z',
        last_sign_in_at: '2024-01-01T12:00:00Z',
      };

      act(() => {
        result.current.setUser(mockUser);
      });

      expect(UserManager.setUser).toHaveBeenCalledWith(mockUser);
      expect(result.current.user).toEqual(mockUser);
      expect(result.current.isAuthenticated).toBe(true);
    });
  });

  describe('clearTokens', () => {
    it('should clear tokens and update authentication state', () => {
      const { result } = renderHook(() => useAuthStore());

      // Set initial state
      act(() => {
        result.current.setTokens('access-token', 'refresh-token', 3600);
      });

      act(() => {
        result.current.clearTokens();
      });

      expect(TokenManager.clearTokens).toHaveBeenCalled();
      expect(result.current.accessToken).toBeNull();
      expect(result.current.refreshToken).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });
  });

  describe('clearUser', () => {
    it('should clear user and update authentication state', () => {
      const { result } = renderHook(() => useAuthStore());
      const mockUser = {
        id: 'test-user-123',
        name: 'Test User',
        email: 'test@example.com',
        avatar_url: '',
        created_at: '2024-01-01T00:00:00Z',
        last_sign_in_at: '2024-01-01T12:00:00Z',
      };

      // Set initial state
      act(() => {
        result.current.setUser(mockUser);
      });

      act(() => {
        result.current.clearUser();
      });

      expect(UserManager.clearUser).toHaveBeenCalled();
      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });
  });

  describe('loadSession', () => {
    it('should load valid session from localStorage', () => {
      const { result } = renderHook(() => useAuthStore());
      const mockUser = {
        id: 'test-user-123',
        name: 'Test User',
        email: 'test@example.com',
        avatar_url: '',
        created_at: '2024-01-01T00:00:00Z',
        last_sign_in_at: '2024-01-01T12:00:00Z',
      };

      // Mock localStorage data
      vi.mocked(TokenManager.getAccessToken).mockReturnValue('access-token');
      vi.mocked(TokenManager.getRefreshToken).mockReturnValue('refresh-token');
      vi.mocked(TokenManager.getTokenExpiry).mockReturnValue(Date.now() + 3600000);
      vi.mocked(TokenManager.isTokenExpired).mockReturnValue(false);
      vi.mocked(UserManager.getUser).mockReturnValue(mockUser);

      act(() => {
        result.current.loadSession();
      });

      expect(result.current.accessToken).toBe('access-token');
      expect(result.current.refreshToken).toBe('refresh-token');
      expect(result.current.user).toEqual(mockUser);
      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.isLoading).toBe(false);
    });

    it('should handle errors during session loading', () => {
      const { result } = renderHook(() => useAuthStore());

      // Mock error
      vi.mocked(TokenManager.getAccessToken).mockImplementation(() => {
        throw new Error('Failed to load session');
      });

      act(() => {
        result.current.loadSession();
      });

      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe('Failed to load session');
    });
  });

  describe('logout', () => {
    it('should clear all authentication data', () => {
      const { result } = renderHook(() => useAuthStore());

      // Set initial state
      act(() => {
        result.current.setTokens('access-token', 'refresh-token', 3600);
        result.current.setUser({
          id: 'test-user-123',
          name: 'Test User',
          email: 'test@example.com',
          avatar_url: '',
          created_at: '2024-01-01T00:00:00Z',
          last_sign_in_at: '2024-01-01T12:00:00Z',
        });
      });

      act(() => {
        result.current.logout();
      });

      expect(TokenManager.clearTokens).toHaveBeenCalled();
      expect(UserManager.clearUser).toHaveBeenCalled();
      expect(result.current.user).toBeNull();
      expect(result.current.accessToken).toBeNull();
      expect(result.current.refreshToken).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('should handle logout errors gracefully', () => {
      const { result } = renderHook(() => useAuthStore());

      // Mock error
      vi.mocked(TokenManager.clearTokens).mockImplementation(() => {
        throw new Error('Failed to logout properly');
      });

      act(() => {
        result.current.logout();
      });

      expect(result.current.error).toBe('Failed to logout properly');
    });
  });
}); 