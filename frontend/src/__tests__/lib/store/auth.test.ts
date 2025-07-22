/**
 * Auth Store Tests
 * 
 * Tests for the authentication store functionality.
 */

import { renderHook, act } from '@testing-library/react';
import { useAuthStore } from '@/lib/store/auth';
import { TokenManager, UserManager } from '@/lib/auth';
import { mockUser } from '../../utils/test-utils';

// Mock the auth utilities
jest.mock('@/lib/auth', () => ({
  TokenManager: {
    getAccessToken: jest.fn(),
    getRefreshToken: jest.fn(),
    getTokenExpiry: jest.fn(),
    setTokens: jest.fn(),
    clearTokens: jest.fn(),
    isTokenExpired: jest.fn(),
    hasValidTokens: jest.fn(),
  },
  UserManager: {
    getUser: jest.fn(),
    setUser: jest.fn(),
    clearUser: jest.fn(),
  },
}));

describe('Auth Store', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const { result } = renderHook(() => useAuthStore());
      
      expect(result.current.user).toBeNull();
      expect(result.current.accessToken).toBeNull();
      expect(result.current.refreshToken).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.isLoading).toBe(true);
      expect(result.current.error).toBeNull();
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
      expect(result.current.error).toBeNull();
    });
  });

  describe('setUser', () => {
    it('should set user and update authentication state', () => {
      const { result } = renderHook(() => useAuthStore());
      
      act(() => {
        result.current.setUser(mockUser);
      });

      expect(UserManager.setUser).toHaveBeenCalledWith(mockUser);
      expect(result.current.user).toEqual(mockUser);
      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.error).toBeNull();
    });
  });

  describe('clearTokens', () => {
    it('should clear tokens and update authentication state', () => {
      const { result } = renderHook(() => useAuthStore());
      
      // Set initial state
      act(() => {
        result.current.setTokens('access-token', 'refresh-token', 3600);
      });

      // Clear tokens
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
      
      // Set initial state
      act(() => {
        result.current.setUser(mockUser);
      });

      // Clear user
      act(() => {
        result.current.clearUser();
      });

      expect(UserManager.clearUser).toHaveBeenCalled();
      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });
  });

  describe('setLoading', () => {
    it('should update loading state', () => {
      const { result } = renderHook(() => useAuthStore());
      
      act(() => {
        result.current.setLoading(false);
      });

      expect(result.current.isLoading).toBe(false);
    });
  });

  describe('setError', () => {
    it('should update error state', () => {
      const { result } = renderHook(() => useAuthStore());
      
      act(() => {
        result.current.setError('Test error message');
      });

      expect(result.current.error).toBe('Test error message');
    });

    it('should clear error when set to null', () => {
      const { result } = renderHook(() => useAuthStore());
      
      // Set error first
      act(() => {
        result.current.setError('Test error message');
      });

      // Clear error
      act(() => {
        result.current.setError(null);
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('loadSession', () => {
    it('should load valid session from localStorage', () => {
      const { result } = renderHook(() => useAuthStore());
      
      // Mock valid tokens and user
      (TokenManager.hasValidTokens as jest.Mock).mockReturnValue(true);
      (TokenManager.getAccessToken as jest.Mock).mockReturnValue('access-token');
      (TokenManager.getRefreshToken as jest.Mock).mockReturnValue('refresh-token');
      (UserManager.getUser as jest.Mock).mockReturnValue(mockUser);

      act(() => {
        result.current.loadSession();
      });

      expect(result.current.accessToken).toBe('access-token');
      expect(result.current.refreshToken).toBe('refresh-token');
      expect(result.current.user).toEqual(mockUser);
      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('should handle invalid session gracefully', () => {
      const { result } = renderHook(() => useAuthStore());
      
      // Mock invalid tokens
      (TokenManager.hasValidTokens as jest.Mock).mockReturnValue(false);

      act(() => {
        result.current.loadSession();
      });

      expect(result.current.user).toBeNull();
      expect(result.current.accessToken).toBeNull();
      expect(result.current.refreshToken).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('should handle errors during session loading', () => {
      const { result } = renderHook(() => useAuthStore());
      
      // Mock error during session loading
      (TokenManager.hasValidTokens as jest.Mock).mockImplementation(() => {
        throw new Error('Storage error');
      });

      act(() => {
        result.current.loadSession();
      });

      expect(result.current.user).toBeNull();
      expect(result.current.accessToken).toBeNull();
      expect(result.current.refreshToken).toBeNull();
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
        result.current.setUser(mockUser);
      });

      // Logout
      act(() => {
        result.current.logout();
      });

      expect(TokenManager.clearTokens).toHaveBeenCalled();
      expect(UserManager.clearUser).toHaveBeenCalled();
      expect(result.current.user).toBeNull();
      expect(result.current.accessToken).toBeNull();
      expect(result.current.refreshToken).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('should handle logout errors gracefully', () => {
      const { result } = renderHook(() => useAuthStore());
      
      // Mock error during logout
      (TokenManager.clearTokens as jest.Mock).mockImplementation(() => {
        throw new Error('Clear error');
      });

      act(() => {
        result.current.logout();
      });

      expect(result.current.error).toBe('Failed to logout properly');
    });
  });
}); 