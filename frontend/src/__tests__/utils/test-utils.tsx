/**
 * Test Utilities
 * 
 * Common test utilities and mocks for authentication system testing.
 */

import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { AuthProvider } from '@/components/auth/AuthProvider';
import type { User } from '@/lib/types';

// Mock the API client
jest.mock('@/lib/api', () => ({
  api: {
    auth: {
      googleLogin: jest.fn(),
      getCurrentUser: jest.fn(),
      logout: jest.fn(),
      refreshToken: jest.fn(),
    },
    projects: {
      getProjects: jest.fn(),
      createProject: jest.fn(),
      getProject: jest.fn(),
      deleteProject: jest.fn(),
      getUploadUrl: jest.fn(),
      getProjectStatus: jest.fn(),
    },
    chat: {
      sendMessage: jest.fn(),
      getMessages: jest.fn(),
      getPreview: jest.fn(),
      getSuggestions: jest.fn(),
    },
    system: {
      healthCheck: jest.fn(),
      systemStatus: jest.fn(),
    },
  },
}));

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    back: jest.fn(),
    forward: jest.fn(),
    refresh: jest.fn(),
  }),
  useSearchParams: () => new URLSearchParams(),
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock window.location
Object.defineProperty(window, 'location', {
  value: {
    href: 'http://localhost:3000',
    assign: jest.fn(),
    replace: jest.fn(),
  },
  writable: true,
});

// Test user data
export const mockUser: User = {
  id: 'test-user-123',
  email: 'test@example.com',
  name: 'Test User',
  avatar_url: 'https://example.com/avatar.jpg',
  created_at: '2024-01-01T00:00:00Z',
  last_sign_in_at: '2024-01-01T12:00:00Z',
};

export const mockAuthResponse = {
  success: true,
  data: {
    user: mockUser,
    access_token: 'mock-access-token',
    refresh_token: 'mock-refresh-token',
    expires_in: 3600,
  },
};

// Custom render function with AuthProvider
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  authState?: {
    isAuthenticated?: boolean;
    user?: User | null;
    isLoading?: boolean;
    error?: string | null;
  };
}

export function renderWithAuth(
  ui: ReactElement,
  options: CustomRenderOptions = {}
) {
  const { authState: _authState, ...renderOptions } = options;

  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <AuthProvider>{children}</AuthProvider>
  );

  return render(ui, { wrapper: Wrapper, ...renderOptions });
}

// Mock auth store
export const mockAuthStore = {
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
  setError: jest.fn(),
  loadSession: jest.fn(),
  logout: jest.fn(),
};

// Mock auth context
export const mockAuthContext = {
  user: null,
  accessToken: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  login: jest.fn(),
  logout: jest.fn(),
  refreshToken: jest.fn(),
  setError: jest.fn(),
};

// Helper to clear all mocks
export const clearAllMocks = () => {
  jest.clearAllMocks();
  localStorageMock.getItem.mockClear();
  localStorageMock.setItem.mockClear();
  localStorageMock.removeItem.mockClear();
  localStorageMock.clear.mockClear();
};

// Helper to set up authenticated state
export const setupAuthenticatedState = () => {
  localStorageMock.getItem
    .mockReturnValueOnce('mock-access-token') // getAccessToken
    .mockReturnValueOnce('mock-refresh-token') // getRefreshToken
    .mockReturnValueOnce((Date.now() + 3600000).toString()) // getTokenExpiry
    .mockReturnValueOnce(JSON.stringify(mockUser)); // getUser
};

// Helper to set up unauthenticated state
export const setupUnauthenticatedState = () => {
  localStorageMock.getItem.mockReturnValue(null);
};

// Helper to wait for async operations
export const waitForAsync = (ms = 0) => new Promise(resolve => setTimeout(resolve, ms));

// Export testing library utilities
export * from '@testing-library/react';
export { default as userEvent } from '@testing-library/user-event'; 