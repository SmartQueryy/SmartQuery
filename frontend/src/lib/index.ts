/**
 * Library Index
 * 
 * Central export point for all lib modules.
 */

// Core infrastructure
export * from './api';
export * from './auth';
export * from './types';
export * from './retry';

// Re-export commonly used types
export type {
  User,
  Project,
  ChatMessage,
  QueryResult,
  ApiResponse,
  PaginatedResponse,
} from './types';

// Re-export commonly used functions
export {
  api,
  authApi,
  projectApi,
  chatApi,
  systemApi,
} from './api';

export {
  getAccessToken,
  setTokens,
  clearTokens,
  refreshToken,
  logout,
  isAuthenticated,
  getCurrentUser,
} from './auth';

export {
  withRetry,
  withTimeout,
} from './retry'; 