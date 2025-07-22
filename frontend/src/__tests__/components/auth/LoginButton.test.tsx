/**
 * LoginButton Tests
 * 
 * Tests for the LoginButton component and OAuth flow.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LoginButton, GoogleLoginButton } from '@/components/auth/LoginButton';
import { useAuth } from '@/components/auth/AuthProvider';
import { api } from '@/lib/api';

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

describe('LoginButton', () => {
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

  describe('Basic Rendering', () => {
    it('should render login button with default props', () => {
      render(<LoginButton />);
      
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
      expect(button).toHaveTextContent('Sign in with Google');
    });

    it('should render with custom children', () => {
      render(<LoginButton>Custom Login Text</LoginButton>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveTextContent('Custom Login Text');
    });

    it('should render Google icon', () => {
      render(<LoginButton />);
      
      const button = screen.getByRole('button');
      const svg = button.querySelector('svg');
      expect(svg).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      render(<LoginButton className="custom-class" />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('custom-class');
    });
  });

  describe('Button Variants', () => {
    it('should render primary variant by default', () => {
      render(<LoginButton />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('btn-primary');
    });

    it('should render secondary variant', () => {
      render(<LoginButton variant="secondary" />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('btn-secondary');
    });

    it('should render outline variant', () => {
      render(<LoginButton variant="outline" />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('btn-outline');
    });
  });

  describe('Button Sizes', () => {
    it('should render medium size by default', () => {
      render(<LoginButton />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('px-4', 'py-2', 'text-base');
    });

    it('should render small size', () => {
      render(<LoginButton size="sm" />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('px-3', 'py-1.5', 'text-sm');
    });

    it('should render large size', () => {
      render(<LoginButton size="lg" />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('px-6', 'py-3', 'text-lg');
    });
  });

  describe('Click Handling', () => {
    it('should redirect to OAuth endpoint on click', () => {
      const originalLocation = window.location;
      delete (window as any).location;
      window.location = { href: '' } as any;

      render(<LoginButton />);
      
      const button = screen.getByRole('button');
      fireEvent.click(button);

      expect(window.location.href).toBe('http://localhost:8000/auth/google');
      
      window.location = originalLocation;
    });

    it('should show loading state during redirect', () => {
      render(<LoginButton />);
      
      const button = screen.getByRole('button');
      fireEvent.click(button);

      expect(button).toBeDisabled();
      expect(screen.getByText('Signing in...')).toBeInTheDocument();
    });

    it('should handle click errors gracefully', () => {
      const mockSetError = jest.fn();
      mockUseAuth.mockReturnValue({
        ...mockUseAuth(),
        setError: mockSetError,
      });

      // Mock window.location.href to throw error
      const originalLocation = window.location;
      delete (window as any).location;
      window.location = { href: '' } as any;
      
      Object.defineProperty(window.location, 'href', {
        set: jest.fn().mockImplementation(() => {
          throw new Error('Redirect failed');
        }),
      });

      render(<LoginButton />);
      
      const button = screen.getByRole('button');
      fireEvent.click(button);

      expect(mockSetError).toHaveBeenCalledWith('Failed to start login process');
      
      window.location = originalLocation;
    });
  });

  describe('OAuth Callback Handling', () => {
    it('should handle OAuth callback with authorization code', async () => {
      const mockLogin = jest.fn();
      const mockSetError = jest.fn();
      
      mockUseAuth.mockReturnValue({
        ...mockUseAuth(),
        login: mockLogin,
        setError: mockSetError,
      });

      // Mock useSearchParams to return a code
      jest.doMock('next/navigation', () => ({
        useRouter: () => ({ push: jest.fn() }),
        useSearchParams: () => new URLSearchParams('?code=auth-code'),
      }));

      (api.auth.googleLogin as jest.Mock).mockResolvedValue({
        success: true,
        data: {
          user: { id: '1', name: 'Test User', email: 'test@example.com' },
          access_token: 'access-token',
          refresh_token: 'refresh-token',
          expires_in: 3600,
        },
      });

      render(<LoginButton />);

      await waitFor(() => {
        expect(api.auth.googleLogin).toHaveBeenCalledWith({
          google_token: 'auth-code',
        });
      });
    });

    it('should handle OAuth callback errors', async () => {
      const mockSetError = jest.fn();
      
      mockUseAuth.mockReturnValue({
        ...mockUseAuth(),
        setError: mockSetError,
      });

      // Mock useSearchParams to return an error
      jest.doMock('next/navigation', () => ({
        useRouter: () => ({ push: jest.fn() }),
        useSearchParams: () => new URLSearchParams('?error=access_denied'),
      }));

      render(<LoginButton />);

      await waitFor(() => {
        expect(mockSetError).toHaveBeenCalledWith('Login failed: access_denied');
      });
    });
  });

  describe('Disabled State', () => {
    it('should be disabled when loading', () => {
      render(<LoginButton />);
      
      const button = screen.getByRole('button');
      fireEvent.click(button);

      expect(button).toBeDisabled();
    });

    it('should show loading spinner when disabled', () => {
      render(<LoginButton />);
      
      const button = screen.getByRole('button');
      fireEvent.click(button);

      const spinner = button.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
    });
  });
});

describe('GoogleLoginButton', () => {
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

  it('should render with Google styling', () => {
    render(<GoogleLoginButton />);
    
    const button = screen.getByRole('button');
    expect(button).toHaveClass('bg-white', 'text-gray-700', 'border', 'border-gray-300');
  });

  it('should render with "Continue with Google" text', () => {
    render(<GoogleLoginButton />);
    
    const button = screen.getByRole('button');
    expect(button).toHaveTextContent('Continue with Google');
  });

  it('should be full width', () => {
    render(<GoogleLoginButton />);
    
    const button = screen.getByRole('button');
    expect(button).toHaveClass('w-full', 'max-w-sm', 'mx-auto');
  });

  it('should handle click events', () => {
    const originalLocation = window.location;
    delete (window as any).location;
    window.location = { href: '' } as any;

    render(<GoogleLoginButton />);
    
    const button = screen.getByRole('button');
    fireEvent.click(button);

    expect(window.location.href).toBe('http://localhost:8000/auth/google');
    
    window.location = originalLocation;
  });
}); 