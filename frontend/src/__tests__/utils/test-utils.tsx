/**
 * Test Utilities
 * 
 * Common test utilities and mocks for authentication system testing.
 */

import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { vi } from 'vitest';
import { AuthProvider } from '@/components/auth/AuthProvider';
import type { User } from '@/lib/types';

// Mock the API client
const mockApi = {
  auth: {
    googleLogin: vi.fn().mockResolvedValue({
      success: true,
      data: {
        user: {
          id: '1',
          name: 'Test User',
          email: 'test@example.com',
          avatar_url: '',
          created_at: '2024-01-01T00:00:00Z',
          last_sign_in_at: '2024-01-01T12:00:00Z',
        },
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
        expires_in: 3600,
      },
    }),
    getCurrentUser: vi.fn().mockResolvedValue({
      success: true,
      data: {
        user: {
          id: '1',
          name: 'Test User',
          email: 'test@example.com',
          avatar_url: '',
          created_at: '2024-01-01T00:00:00Z',
          last_sign_in_at: '2024-01-01T12:00:00Z',
        },
      },
    }),
    logout: vi.fn().mockResolvedValue({ success: true }),
    refreshToken: vi.fn().mockResolvedValue({
      success: true,
      data: {
        access_token: 'new-access-token',
        refresh_token: 'new-refresh-token',
        expires_in: 3600,
      },
    }),
  },
  projects: {
    getProjects: vi.fn().mockResolvedValue({
      success: true,
      data: [
        {
          id: '1',
          name: 'Test Project',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ],
    }),
    createProject: vi.fn().mockResolvedValue({
      success: true,
      data: {
        id: '1',
        name: 'Test Project',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    }),
    getProject: vi.fn().mockResolvedValue({
      success: true,
      data: {
        id: '1',
        name: 'Test Project',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    }),
    deleteProject: vi.fn().mockResolvedValue({ success: true }),
    getUploadUrl: vi.fn().mockResolvedValue({
      success: true,
      data: { upload_url: 'https://example.com/upload' },
    }),
    getProjectStatus: vi.fn().mockResolvedValue({
      success: true,
      data: { status: 'completed' },
    }),
  },
  chat: {
    sendMessage: vi.fn().mockResolvedValue({
      success: true,
      data: {
        message: 'Test response',
        result_type: 'text',
        result: 'Test result',
      },
    }),
    getMessages: vi.fn().mockResolvedValue({
      success: true,
      data: [
        {
          id: '1',
          message: 'Test message',
          response: 'Test response',
          created_at: '2024-01-01T00:00:00Z',
        },
      ],
    }),
    getPreview: vi.fn().mockResolvedValue({
      success: true,
      data: {
        headers: ['col1', 'col2'],
        rows: [['val1', 'val2']],
      },
    }),
    getSuggestions: vi.fn().mockResolvedValue({
      success: true,
      data: ['suggestion1', 'suggestion2'],
    }),
  },
  system: {
    healthCheck: vi.fn().mockResolvedValue({ success: true }),
    systemStatus: vi.fn().mockResolvedValue({
      success: true,
      data: { status: 'healthy' },
    }),
  },
};

vi.mock('@/lib/api', () => ({
  api: mockApi,
}));

// Mock Next.js router
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    refresh: vi.fn(),
  }),
  useSearchParams: () => new URLSearchParams(),
}));

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock window.location
Object.defineProperty(window, 'location', {
  value: {
    href: 'http://localhost:3000',
    assign: vi.fn(),
    replace: vi.fn(),
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
  setTokens: vi.fn(),
  setUser: vi.fn(),
  clearTokens: vi.fn(),
  clearUser: vi.fn(),
  setLoading: vi.fn(),
  setError: vi.fn(),
  loadSession: vi.fn(),
  logout: vi.fn(),
};

// Mock auth context
export const mockAuthContext = {
  user: null,
  accessToken: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  login: vi.fn(),
  logout: vi.fn(),
  refreshToken: vi.fn(),
  setError: vi.fn(),
};

// Helper to clear all mocks
export const clearAllMocks = () => {
  vi.clearAllMocks();
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