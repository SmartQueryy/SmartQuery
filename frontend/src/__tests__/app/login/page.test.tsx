/**
 * Login Page Integration Tests
 * 
 * Integration tests for the login page and authentication flow.
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import LoginPage from '@/app/login/page';
import { useAuth } from '@/components/auth/AuthProvider';

// Mock the auth context
jest.mock('@/components/auth/AuthProvider', () => ({
  useAuth: jest.fn(),
}));

// Mock Next.js navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
  useSearchParams: () => new URLSearchParams(),
}));

const mockUseAuth = useAuth as jest.MockedFunction<typeof useAuth>;

describe('Login Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockUseAuth.mockReturnValue({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      login: jest.fn(),
      logout: jest.fn(),
      refreshToken: jest.fn(),
      setError: jest.fn(),
    });
  });

  describe('Page Rendering', () => {
    it('should render login page with SmartQuery branding', () => {
      render(<LoginPage />);

      expect(screen.getByText('Welcome to SmartQuery')).toBeInTheDocument();
      expect(screen.getByText('Sign in to access your data analysis dashboard')).toBeInTheDocument();
    });

    it('should render Google login buttons', () => {
      render(<LoginPage />);

      expect(screen.getByText('Continue with Google')).toBeInTheDocument();
      expect(screen.getByText('Sign in with Google')).toBeInTheDocument();
    });

    it('should render features preview section', () => {
      render(<LoginPage />);

      expect(screen.getByText('What you can do with SmartQuery')).toBeInTheDocument();
      expect(screen.getByText(/Upload and analyze CSV files/)).toBeInTheDocument();
      expect(screen.getByText(/Generate interactive charts/)).toBeInTheDocument();
      expect(screen.getByText(/Get instant insights/)).toBeInTheDocument();
    });

    it('should render terms and privacy links', () => {
      render(<LoginPage />);

      expect(screen.getByText('Terms of Service')).toBeInTheDocument();
      expect(screen.getByText('Privacy Policy')).toBeInTheDocument();
    });
  });

  describe('Authentication States', () => {
    it('should redirect to dashboard when already authenticated', () => {
      const mockPush = jest.fn();
      jest.doMock('next/navigation', () => ({
        useRouter: () => ({ push: mockPush }),
        useSearchParams: () => new URLSearchParams(),
      }));

      mockUseAuth.mockReturnValue({
        user: { id: '1', name: 'Test User', email: 'test@example.com' },
        accessToken: 'token',
        isAuthenticated: true,
        isLoading: false,
        error: null,
        login: jest.fn(),
        logout: jest.fn(),
        refreshToken: jest.fn(),
        setError: jest.fn(),
      });

      render(<LoginPage />);

      expect(mockPush).toHaveBeenCalledWith('/dashboard');
    });

    it('should show error message when authentication fails', () => {
      const mockSetError = jest.fn();
      mockUseAuth.mockReturnValue({
        user: null,
        accessToken: null,
        isAuthenticated: false,
        isLoading: false,
        error: 'Authentication failed',
        login: jest.fn(),
        logout: jest.fn(),
        refreshToken: jest.fn(),
        setError: mockSetError,
      });

      render(<LoginPage />);

      expect(screen.getByText('Authentication Error')).toBeInTheDocument();
      expect(screen.getByText('Authentication failed')).toBeInTheDocument();
    });

    it('should handle OAuth errors from URL parameters', () => {
      const mockSetError = jest.fn();
      mockUseAuth.mockReturnValue({
        user: null,
        accessToken: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
        login: jest.fn(),
        logout: jest.fn(),
        refreshToken: jest.fn(),
        setError: mockSetError,
      });

      // Mock useSearchParams to return an error
      jest.doMock('next/navigation', () => ({
        useRouter: () => ({ push: jest.fn() }),
        useSearchParams: () => new URLSearchParams('?error=access_denied'),
      }));

      render(<LoginPage />);

      expect(mockSetError).toHaveBeenCalledWith('Login failed: access_denied');
    });
  });

  describe('Button Interactions', () => {
    it('should handle Google login button clicks', () => {
      const originalLocation = window.location;
      delete (window as any).location;
      window.location = { href: '' } as any;

      render(<LoginPage />);

      const googleButton = screen.getByText('Continue with Google');
      fireEvent.click(googleButton);

      expect(window.location.href).toBe('http://localhost:8000/auth/google');

      window.location = originalLocation;
    });

    it('should handle alternative login button clicks', () => {
      const originalLocation = window.location;
      delete (window as any).location;
      window.location = { href: '' } as any;

      render(<LoginPage />);

      const altButton = screen.getByText('Sign in with Google');
      fireEvent.click(altButton);

      expect(window.location.href).toBe('http://localhost:8000/auth/google');

      window.location = originalLocation;
    });
  });

  describe('Page Layout', () => {
    it('should have proper responsive layout', () => {
      render(<LoginPage />);

      const container = screen.getByText('Welcome to SmartQuery').closest('div');
      expect(container).toHaveClass('min-h-screen', 'bg-gradient-to-br', 'from-blue-50', 'to-indigo-100');
    });

    it('should have proper card styling', () => {
      render(<LoginPage />);

      const loginCard = screen.getByText('Continue with Google').closest('div');
      expect(loginCard).toHaveClass('bg-white', 'py-8', 'px-6', 'shadow-xl', 'rounded-lg');
    });

    it('should have proper button styling', () => {
      render(<LoginPage />);

      const googleButton = screen.getByText('Continue with Google');
      expect(googleButton).toHaveClass('w-full', 'max-w-sm', 'mx-auto', 'bg-white', 'text-gray-700');
    });
  });

  describe('Accessibility', () => {
    it('should have proper button roles', () => {
      render(<LoginPage />);

      const buttons = screen.getAllByRole('button');
      expect(buttons).toHaveLength(2); // Two login buttons
    });

    it('should have proper heading structure', () => {
      render(<LoginPage />);

      const mainHeading = screen.getByRole('heading', { level: 1 });
      expect(mainHeading).toHaveTextContent('Welcome to SmartQuery');

      const subHeading = screen.getByRole('heading', { level: 3 });
      expect(subHeading).toHaveTextContent('What you can do with SmartQuery');
    });

    it('should have proper link elements', () => {
      render(<LoginPage />);

      const links = screen.getAllByRole('link');
      expect(links).toHaveLength(2); // Terms and Privacy links
    });
  });
}); 