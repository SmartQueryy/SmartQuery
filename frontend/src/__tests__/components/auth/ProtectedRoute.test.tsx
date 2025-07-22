/**
 * ProtectedRoute Tests
 * 
 * Tests for the ProtectedRoute component and route protection.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { ProtectedRoute, withAuth, useProtectedRoute, AuthGuard } from '@/components/auth/ProtectedRoute';
import { useAuth } from '@/components/auth/AuthProvider';

// Mock the auth context
jest.mock('@/components/auth/AuthProvider', () => ({
  useAuth: jest.fn(),
}));

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

const mockUseAuth = useAuth as jest.MockedFunction<typeof useAuth>;

describe('ProtectedRoute', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const TestComponent = () => <div>Protected Content</div>;

  describe('Authentication States', () => {
    it('should render children when authenticated', () => {
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

      render(
        <ProtectedRoute>
          <TestComponent />
        </ProtectedRoute>
      );

      expect(screen.getByText('Protected Content')).toBeInTheDocument();
    });

    it('should redirect to login when not authenticated', () => {
      const mockPush = jest.fn();
      jest.doMock('next/navigation', () => ({
        useRouter: () => ({ push: mockPush }),
      }));

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

      render(
        <ProtectedRoute>
          <TestComponent />
        </ProtectedRoute>
      );

      expect(mockPush).toHaveBeenCalledWith('/login');
    });

    it('should show loading state while checking authentication', () => {
      mockUseAuth.mockReturnValue({
        user: null,
        accessToken: null,
        isAuthenticated: false,
        isLoading: true,
        error: null,
        login: jest.fn(),
        logout: jest.fn(),
        refreshToken: jest.fn(),
        setError: jest.fn(),
      });

      render(
        <ProtectedRoute>
          <TestComponent />
        </ProtectedRoute>
      );

      expect(screen.getByText('Loading...')).toBeInTheDocument();
      expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
    });

    it('should redirect to custom path when specified', () => {
      const mockPush = jest.fn();
      jest.doMock('next/navigation', () => ({
        useRouter: () => ({ push: mockPush }),
      }));

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

      render(
        <ProtectedRoute redirectTo="/custom-login">
          <TestComponent />
        </ProtectedRoute>
      );

      expect(mockPush).toHaveBeenCalledWith('/custom-login');
    });
  });

  describe('Custom Fallback', () => {
    it('should render custom fallback when loading', () => {
      mockUseAuth.mockReturnValue({
        user: null,
        accessToken: null,
        isAuthenticated: false,
        isLoading: true,
        error: null,
        login: jest.fn(),
        logout: jest.fn(),
        refreshToken: jest.fn(),
        setError: jest.fn(),
      });

      const CustomFallback = () => <div>Custom Loading...</div>;

      render(
        <ProtectedRoute fallback={<CustomFallback />}>
          <TestComponent />
        </ProtectedRoute>
      );

      expect(screen.getByText('Custom Loading...')).toBeInTheDocument();
    });

    it('should render custom fallback when not authenticated', () => {
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

      const CustomFallback = () => <div>Please log in to continue</div>;

      render(
        <ProtectedRoute fallback={<CustomFallback />}>
          <TestComponent />
        </ProtectedRoute>
      );

      expect(screen.getByText('Please log in to continue')).toBeInTheDocument();
    });
  });
});

describe('withAuth HOC', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const TestComponent = () => <div>Protected Component</div>;

  it('should wrap component with ProtectedRoute', () => {
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

    const ProtectedComponent = withAuth(TestComponent);
    render(<ProtectedComponent />);

    expect(screen.getByText('Protected Component')).toBeInTheDocument();
  });

  it('should pass props to wrapped component', () => {
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

    const TestComponentWithProps = ({ message }: { message: string }) => (
      <div>Message: {message}</div>
    );

    const ProtectedComponent = withAuth(TestComponentWithProps);
    render(<ProtectedComponent message="Hello World" />);

    expect(screen.getByText('Message: Hello World')).toBeInTheDocument();
  });
});

describe('useProtectedRoute Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should return authentication state', () => {
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

    const TestComponent = () => {
      const { isAuthenticated, isLoading, canAccess } = useProtectedRoute();
      return (
        <div>
          <div data-testid="isAuthenticated">{isAuthenticated.toString()}</div>
          <div data-testid="isLoading">{isLoading.toString()}</div>
          <div data-testid="canAccess">{canAccess.toString()}</div>
        </div>
      );
    };

    render(<TestComponent />);

    expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('true');
    expect(screen.getByTestId('isLoading')).toHaveTextContent('false');
    expect(screen.getByTestId('canAccess')).toHaveTextContent('true');
  });

  it('should redirect when not authenticated', () => {
    const mockPush = jest.fn();
    jest.doMock('next/navigation', () => ({
      useRouter: () => ({ push: mockPush }),
    }));

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

    const TestComponent = () => {
      useProtectedRoute();
      return <div>Test</div>;
    };

    render(<TestComponent />);

    expect(mockPush).toHaveBeenCalledWith('/login');
  });
});

describe('AuthGuard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const TestComponent = () => <div>Guarded Content</div>;

  it('should render children when authenticated', () => {
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

    render(
      <AuthGuard>
        <TestComponent />
      </AuthGuard>
    );

    expect(screen.getByText('Guarded Content')).toBeInTheDocument();
  });

  it('should show loading state while checking authentication', () => {
    mockUseAuth.mockReturnValue({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      isLoading: true,
      error: null,
      login: jest.fn(),
      logout: jest.fn(),
      refreshToken: jest.fn(),
      setError: jest.fn(),
    });

    render(
      <AuthGuard>
        <TestComponent />
      </AuthGuard>
    );

    const spinner = screen.getByRole('status', { hidden: true });
    expect(spinner).toBeInTheDocument();
  });

  it('should not render children when not authenticated', () => {
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

    render(
      <AuthGuard>
        <TestComponent />
      </AuthGuard>
    );

    expect(screen.queryByText('Guarded Content')).not.toBeInTheDocument();
  });

  it('should render custom fallback when loading', () => {
    mockUseAuth.mockReturnValue({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      isLoading: true,
      error: null,
      login: jest.fn(),
      logout: jest.fn(),
      refreshToken: jest.fn(),
      setError: jest.fn(),
    });

    const CustomFallback = () => <div>Custom Loading...</div>;

    render(
      <AuthGuard fallback={<CustomFallback />}>
        <TestComponent />
      </AuthGuard>
    );

    expect(screen.getByText('Custom Loading...')).toBeInTheDocument();
  });
}); 