# SmartQuery Frontend Library

This directory contains the core infrastructure for the SmartQuery frontend application.

## Files Overview

### Core Infrastructure

- **`api.ts`** - Central API client with axios, interceptors, and type-safe API calls
- **`auth.ts`** - Authentication utilities for JWT token management
- **`types.ts`** - TypeScript type definitions matching the API contract
- **`retry.ts`** - Retry and timeout utilities with exponential backoff
- **`index.ts`** - Central export point for all modules

## Features

### API Client (`api.ts`)

- ✅ Axios-based HTTP client with interceptors
- ✅ Automatic JWT token injection
- ✅ Token refresh on 401 responses
- ✅ Retry logic with exponential backoff
- ✅ Per-request timeout support
- ✅ Type-safe API calls using the contract
- ✅ Standardized error handling

### Authentication (`auth.ts`)

- ✅ JWT token management (access + refresh)
- ✅ LocalStorage-based token persistence
- ✅ Token expiry checking
- ✅ Automatic token refresh
- ✅ User session management
- ✅ Secure logout with token revocation

### Type Safety (`types.ts`)

- ✅ Complete API contract types
- ✅ Request/response type definitions
- ✅ Frontend-specific utility types
- ✅ Type-safe API endpoint mapping
- ✅ Comprehensive error types

### Retry Logic (`retry.ts`)

- ✅ Exponential backoff (500ms → 1000ms → 2000ms)
- ✅ Configurable retry attempts (default: 3)
- ✅ Timeout fallback (default: 10s)
- ✅ Smart error classification (don't retry 4xx errors)
- ✅ Utility functions for wrapping async operations

## Usage Examples

### Making API Calls

```typescript
import { api } from "@/lib";

// Get user projects
const projects = await api.projects.getProjects({ page: 1, limit: 10 });

// Create a new project
const newProject = await api.projects.createProject({
  name: "My Dataset",
  description: "Sales data analysis",
});

// Send a chat message
const response = await api.chat.sendMessage({
  project_id: "project-123",
  message: "Show me total sales by month",
});
```

### Authentication

```typescript
import { getAccessToken, isAuthenticated, logout } from "@/lib";

// Check if user is authenticated
if (isAuthenticated()) {
  // User is logged in
}

// Get current access token
const token = getAccessToken();

// Logout user
await logout();
```

### Retry Logic

```typescript
import { withRetry, withTimeout } from "@/lib";

// Wrap function with retry logic
const result = await withRetry(() => fetch("/api/data"), {
  maxRetries: 3,
  timeoutMs: 5000,
});

// Wrap promise with timeout
const data = await withTimeout(
  fetch("/api/slow-endpoint"),
  10000 // 10 second timeout
);
```

## Configuration

### Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id
```

### Default Settings

- **API Timeout**: 30 seconds
- **Retry Attempts**: 3
- **Base Retry Delay**: 500ms
- **Max Retry Delay**: 10 seconds
- **Token Refresh Buffer**: 30 seconds

## Error Handling

The API client provides standardized error handling:

```typescript
try {
  const data = await api.projects.getProjects({});
} catch (error) {
  // Error is automatically formatted and includes:
  // - HTTP status code
  // - Error message from API
  // - Validation errors (if any)
  console.error(error.message);
}
```

## Type Safety

All API calls are fully type-safe:

```typescript
// TypeScript will enforce correct request/response types
const response = await api.auth.googleLogin({
  google_token: "valid-google-token",
});

// response.data.user is typed as User
// response.data.access_token is typed as string
```

## Testing

The infrastructure is designed to be easily testable:

```typescript
// Mock the API client for testing
jest.mock("@/lib/api", () => ({
  api: {
    projects: {
      getProjects: jest.fn().mockResolvedValue({
        success: true,
        data: { items: [], total: 0, page: 1, limit: 10, hasMore: false },
      }),
    },
  },
}));
```

## Next Steps

This infrastructure provides the foundation for:

1. **Authentication System** - Google OAuth integration
2. **Project Management** - CRUD operations for datasets
3. **Chat Interface** - Natural language query processing
4. **Data Visualization** - Chart and table rendering
5. **File Upload** - CSV file processing
6. **Real-time Updates** - WebSocket integration (future)

The modular design allows for easy extension and maintenance as the application grows.
