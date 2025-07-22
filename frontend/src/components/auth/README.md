# Authentication System

This directory contains the complete authentication system for SmartQuery, implementing Google OAuth with JWT tokens and React Context for state management.

## Files Overview

### Core Components

- **`AuthProvider.tsx`** - React Context provider for authentication state
- **`LoginButton.tsx`** - Google OAuth login button component
- **`ProtectedRoute.tsx`** - Route guard for protected pages
- **`page.tsx`** - Login page with OAuth integration

### State Management

- **`../lib/store/auth.ts`** - Zustand store for authentication state persistence

## Features

### ✅ Google OAuth Integration

- Client-side redirect flow to backend OAuth endpoint
- Authorization code exchange for JWT tokens
- Automatic token refresh on expiry
- Secure logout with server-side token revocation

### ✅ JWT Token Management

- Access token and refresh token storage
- Automatic token refresh on 401 responses
- Token expiry checking with 30-second buffer
- LocalStorage persistence with Zustand

### ✅ React Context Integration

- Global authentication state management
- Automatic session restoration on app load
- Token verification with server on mount
- Loading states and error handling

### ✅ Route Protection

- Protected route component for page-level guards
- Automatic redirect to login for unauthenticated users
- Loading states during authentication checks
- Higher-order component support

### ✅ Session Persistence

- LocalStorage-based session storage
- Automatic session restoration
- Secure token storage and cleanup
- Cross-tab session synchronization

## Usage Examples

### Basic Authentication Check

```tsx
import { useAuth } from "@/components/auth/AuthProvider";

function MyComponent() {
  const { isAuthenticated, user, logout } = useAuth();

  if (!isAuthenticated) {
    return <div>Please log in</div>;
  }

  return (
    <div>
      <p>Welcome, {user?.name}!</p>
      <button onClick={logout}>Sign Out</button>
    </div>
  );
}
```

### Protected Route

```tsx
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";

function DashboardPage() {
  return (
    <ProtectedRoute>
      <div>Protected content here</div>
    </ProtectedRoute>
  );
}
```

### Login Button

```tsx
import { LoginButton } from "@/components/auth/LoginButton";

function LoginPage() {
  return (
    <div>
      <LoginButton variant="primary" size="lg" redirectTo="/dashboard">
        Sign in with Google
      </LoginButton>
    </div>
  );
}
```

### Higher-Order Component

```tsx
import { withAuth } from "@/components/auth/ProtectedRoute";

function MyProtectedComponent() {
  return <div>Protected content</div>;
}

export default withAuth(MyProtectedComponent);
```

## Authentication Flow

1. **Initial Load**

   - AuthProvider loads session from localStorage
   - Verifies tokens with server via `/auth/me` endpoint
   - Updates authentication state

2. **Login Process**

   - User clicks login button
   - Redirects to backend OAuth endpoint
   - Backend handles Google OAuth flow
   - Returns authorization code to frontend
   - Frontend exchanges code for JWT tokens
   - Stores tokens and user data
   - Redirects to dashboard

3. **Token Refresh**

   - API client detects 401 responses
   - Automatically calls refresh endpoint
   - Updates tokens in store
   - Retries original request

4. **Logout Process**
   - Calls server logout endpoint
   - Clears local tokens and user data
   - Redirects to login page

## Configuration

### Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id
```

### Backend OAuth Endpoints

- `POST /auth/google` - Exchange authorization code for tokens
- `GET /auth/me` - Get current user information
- `POST /auth/logout` - Logout and revoke tokens
- `POST /auth/refresh` - Refresh access token

## Security Features

- **Token Storage**: Secure localStorage with Zustand persistence
- **Token Refresh**: Automatic refresh with request deduplication
- **Server Verification**: Token validation on app mount
- **Secure Logout**: Server-side token revocation
- **Error Handling**: Comprehensive error states and user feedback

## Error Handling

The authentication system handles various error scenarios:

- **Network Errors**: Automatic retry with exponential backoff
- **Token Expiry**: Automatic refresh or logout
- **OAuth Errors**: User-friendly error messages
- **Server Errors**: Graceful degradation and fallback

## Testing

The authentication system is designed to be easily testable:

```tsx
// Mock the auth context for testing
jest.mock("@/components/auth/AuthProvider", () => ({
  useAuth: () => ({
    isAuthenticated: true,
    user: { id: "1", name: "Test User", email: "test@example.com" },
    logout: jest.fn(),
  }),
}));
```

## Next Steps

This authentication system provides the foundation for:

1. **User Profile Management** - User settings and preferences
2. **Role-Based Access Control** - Different permission levels
3. **Multi-Factor Authentication** - Additional security layers
4. **Session Management** - Active session tracking
5. **Audit Logging** - Authentication event tracking

The system is modular and extensible, allowing for easy addition of new authentication methods or security features.
