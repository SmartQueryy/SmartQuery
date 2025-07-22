/**
 * AuthProvider Tests
 * 
 * Tests for the AuthProvider component and its hooks.
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth, useIsAuthenticated, useCurrentUser, useAccessToken } from '@/components/auth/AuthProvider';
import { api } from '@/lib/api';
import { mockUser } from '../../utils/test-utils';

// Mock the auth store
jest.mock('@/lib/store/auth', () => ({
  useAuthStore: jest.fn(),
}));

// Mock the auth utilities
jest.mock('@/lib/auth', () => ({
  refreshToken: jest.fn(),
  logout: jest.fn(),
}));

const mockUseAuthStore = require('@/lib/store/auth').useAuthStore;

describe('AuthProvider', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const TestComponent = () => {
    const auth = useAuth();
    return (
      <div>
        <div data-testid="isAuthenticated">{auth.isAuthenticated.toString()}</div>
        <div data-testid="isLoading">{auth.isLoading.toString()}</div>
        <div data-testid="error">{auth.error || 'no-error'}</div>
        <div data-testid="user-name">{auth.user?.name || 'no-user'}</div>
        <button onClick={() => auth.login(mockUser, { accessToken: 'token', refreshToken: 'refresh', expiresAt: Date.now() + 3600000 })}>
          Login
        </button>
        <button onClick={() => auth.logout()}>Logout</button>
      </div>
    );
  };

  describe('Initialization', () => {
    it('should initialize with default state', () => {
      mockUseAuthStore.mockReturnValue({
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        isLoading: true,
        error: null,
        setTokens: jest.fn(),
        setUser: jest.fn(),
        clearTokens: jest.fn(),
        clearUser: jest.fn(),
        setLoading: jest.fn(),
        setError: jest.fn(),
        loadSession: jest.fn(),
        logout: jest.fn(),
      });

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('false');
      expect(screen.getByTestId('isLoading')).toHaveTextContent('true');
      expect(screen.getByTestId('error')).toHaveTextContent('no-error');
      expect(screen.getByTestId('user-name')).toHaveTextContent('no-user');
    });

    it('should load session on mount', () => {
      const mockLoadSession = jest.fn();
      mockUseAuthStore.mockReturnValue({
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        isLoading: true,
        error: null,
        setTokens: jest.fn(),
        setUser: jest.fn(),
        clearTokens: jest.fn(),
        clearUser: jest.fn(),
        setLoading: jest.fn(),
        setError: jest.fn(),
        loadSession: mockLoadSession,
        logout: jest.fn(),
      });

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      expect(mockLoadSession).toHaveBeenCalled();
    });

    it('should verify tokens with server when authenticated', async () => {
      const mockSetUser = jest.fn();
      const mockSetLoading = jest.fn();
      
      mockUseAuthStore.mockReturnValue({
        user: mockUser,
        accessToken: 'valid-token',
        refreshToken: 'refresh-token',
        isAuthenticated: true,
        isLoading: false,
        error: null,
        setTokens: jest.fn(),
        setUser: mockSetUser,
        clearTokens: jest.fn(),
        clearUser: jest.fn(),
        setLoading: mockSetLoading,
        setError: jest.fn(),
        loadSession: jest.fn(),
        logout: jest.fn(),
      });

      (api.auth.getCurrentUser as jest.Mock).mockResolvedValue({
        success: true,
        data: mockUser,
      });

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(api.auth.getCurrentUser).toHaveBeenCalled();
        expect(mockSetUser).toHaveBeenCalledWith(mockUser);
      });
    });

    it('should handle token verification failure', async () => {
      const mockLogout = jest.fn();
      
      mockUseAuthStore.mockReturnValue({
        user: mockUser,
        accessToken: 'invalid-token',
        refreshToken: 'refresh-token',
        isAuthenticated: true,
        isLoading: false,
        error: null,
        setTokens: jest.fn(),
        setUser: jest.fn(),
        clearTokens: jest.fn(),
        clearUser: jest.fn(),
        setLoading: jest.fn(),
        setError: jest.fn(),
        loadSession: jest.fn(),
        logout: mockLogout,
      });

      (api.auth.getCurrentUser as jest.Mock).mockRejectedValue(new Error('Token invalid'));

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(mockLogout).toHaveBeenCalled();
      });
    });
  });

  describe('Login Function', () => {
    it('should handle login with user and tokens', () => {
      const mockSetUser = jest.fn();
      const mockSetTokens = jest.fn();
      const mockSetError = jest.fn();
      
      mockUseAuthStore.mockReturnValue({
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
        setTokens: mockSetTokens,
        setUser: mockSetUser,
        clearTokens: jest.fn(),
        clearUser: jest.fn(),
        setLoading: jest.fn(),
        setError: mockSetError,
        loadSession: jest.fn(),
        logout: jest.fn(),
      });

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      const loginButton = screen.getByText('Login');
      loginButton.click();

      expect(mockSetUser).toHaveBeenCalledWith(mockUser);
      expect(mockSetTokens).toHaveBeenCalledWith('token', 'refresh', 3600000);
      expect(mockSetError).toHaveBeenCalledWith(null);
    });

    it('should handle login errors', () => {
      const mockSetError = jest.fn();
      
      mockUseAuthStore.mockReturnValue({
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
        setTokens: jest.fn(),
        setUser: jest.fn(),
        clearTokens: jest.fn(),
        clearUser: jest.fn(),
        setLoading: jest.fn(),
        setError: mockSetError,
        loadSession: jest.fn(),
        logout: jest.fn(),
      });

      // Mock error during login
      const mockSetUser = jest.fn().mockImplementation(() => {
        throw new Error('Login failed');
      });

      mockUseAuthStore.mockReturnValue({
        ...mockUseAuthStore(),
        setUser: mockSetUser,
        setError: mockSetError,
      });

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      const loginButton = screen.getByText('Login');
      loginButton.click();

      expect(mockSetError).toHaveBeenCalledWith('Failed to complete login');
    });
  });

  describe('Logout Function', () => {
    it('should handle logout successfully', async () => {
      const mockClearTokens = jest.fn();
      const mockClearUser = jest.fn();
      const mockSetError = jest.fn();
      const mockSetLoading = jest.fn();
      
      mockUseAuthStore.mockReturnValue({
        user: mockUser,
        accessToken: 'token',
        refreshToken: 'refresh',
        isAuthenticated: true,
        isLoading: false,
        error: null,
        setTokens: jest.fn(),
        setUser: jest.fn(),
        clearTokens: mockClearTokens,
        clearUser: mockClearUser,
        setLoading: mockSetLoading,
        setError: mockSetError,
        loadSession: jest.fn(),
        logout: jest.fn(),
      });

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      const logoutButton = screen.getByText('Logout');
      logoutButton.click();

      await waitFor(() => {
        expect(mockSetLoading).toHaveBeenCalledWith(true);
        expect(mockClearTokens).toHaveBeenCalled();
        expect(mockClearUser).toHaveBeenCalled();
        expect(mockSetError).toHaveBeenCalledWith(null);
      });
    });

    it('should handle logout errors gracefully', async () => {
      const mockSetError = jest.fn();
      const mockSetLoading = jest.fn();
      
      mockUseAuthStore.mockReturnValue({
        user: mockUser,
        accessToken: 'token',
        refreshToken: 'refresh',
        isAuthenticated: true,
        isLoading: false,
        error: null,
        setTokens: jest.fn(),
        setUser: jest.fn(),
        clearTokens: jest.fn().mockImplementation(() => {
          throw new Error('Clear error');
        }),
        clearUser: jest.fn(),
        setLoading: mockSetLoading,
        setError: mockSetError,
        loadSession: jest.fn(),
        logout: jest.fn(),
      });

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      const logoutButton = screen.getByText('Logout');
      logoutButton.click();

      await waitFor(() => {
        expect(mockSetError).toHaveBeenCalledWith('Failed to logout properly');
      });
    });
  });

  describe('Hook Exports', () => {
    it('should export useAuth hook', () => {
      expect(useAuth).toBeDefined();
      expect(typeof useAuth).toBe('function');
    });

    it('should export useIsAuthenticated hook', () => {
      expect(useIsAuthenticated).toBeDefined();
      expect(typeof useIsAuthenticated).toBe('function');
    });

    it('should export useCurrentUser hook', () => {
      expect(useCurrentUser).toBeDefined();
      expect(typeof useCurrentUser).toBe('function');
    });

    it('should export useAccessToken hook', () => {
      expect(useAccessToken).toBeDefined();
      expect(typeof useAccessToken).toBe('function');
    });
  });
}); 