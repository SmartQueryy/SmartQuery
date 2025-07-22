/**
 * Central API Client
 * 
 * Axios-based HTTP client with interceptors for authentication,
 * automatic token refresh, retry logic, and type-safe API calls.
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';
import { withRetry, RetryOptions } from './retry';
import { getAccessToken, refreshToken, clearTokens } from './auth';
import type {
  ApiResponse,
  ApiEndpoint,
  ApiRequest,
  ApiResponseType,
} from './types';
import { HttpStatus } from './types';

/**
 * API client configuration
 */
interface ApiClientConfig {
  baseURL: string;
  timeout: number;
  retryOptions: RetryOptions;
}

/**
 * Default API client configuration
 */
const DEFAULT_CONFIG: ApiClientConfig = {
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 30000,
  retryOptions: {
    maxRetries: 3,
    baseDelay: 500,
    maxDelay: 10000,
    backoffMultiplier: 2,
    timeoutMs: 30000,
  },
};

/**
 * API Client class with interceptors and type safety
 */
export class ApiClient {
  private client: AxiosInstance;
  private config: ApiClientConfig;
  private isRefreshing = false;
  private refreshSubscribers: Array<(token: string) => void> = [];

  constructor(config: Partial<ApiClientConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.client = this.createAxiosInstance();
    this.setupInterceptors();
  }

  /**
   * Create axios instance with default configuration
   */
  private createAxiosInstance(): AxiosInstance {
    return axios.create({
      baseURL: this.config.baseURL,
      timeout: this.config.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Setup request and response interceptors
   */
  private setupInterceptors(): void {
    // Request interceptor - add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor - handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

        if (error.response?.status === HttpStatus.UNAUTHORIZED && !originalRequest._retry) {
          if (this.isRefreshing) {
            // Wait for the token refresh to complete
            return new Promise((resolve) => {
              this.refreshSubscribers.push((token: string) => {
                originalRequest.headers = originalRequest.headers || {};
                originalRequest.headers.Authorization = `Bearer ${token}`;
                resolve(this.client(originalRequest));
              });
            });
          }

          originalRequest._retry = true;
          this.isRefreshing = true;

          try {
            const tokens = await refreshToken();
            this.onTokenRefreshed(tokens.accessToken);
            originalRequest.headers = originalRequest.headers || {};
            originalRequest.headers.Authorization = `Bearer ${tokens.accessToken}`;
            return this.client(originalRequest);
          } catch (refreshError) {
            this.onTokenRefreshFailed();
            return Promise.reject(refreshError);
          } finally {
            this.isRefreshing = false;
          }
        }

        return Promise.reject(error);
      }
    );
  }

  /**
   * Handle successful token refresh
   */
  private onTokenRefreshed(token: string): void {
    this.refreshSubscribers.forEach((callback) => callback(token));
    this.refreshSubscribers = [];
  }

  /**
   * Handle failed token refresh
   */
  private onTokenRefreshFailed(): void {
    clearTokens();
    this.refreshSubscribers.forEach((callback) => callback(''));
    this.refreshSubscribers = [];
  }

  /**
   * Make a type-safe API request with retry logic
   */
  async request<T extends ApiEndpoint>(
    endpoint: T,
    requestData: ApiRequest<T>,
    options: {
      timeout?: number;
      retryOptions?: RetryOptions;
      headers?: Record<string, string>;
    } = {}
  ): Promise<ApiResponseType<T>> {
    const { method, url, data, params } = this.parseEndpoint(endpoint, requestData);
    
    const config: AxiosRequestConfig = {
      method,
      url,
      data,
      params,
      timeout: options.timeout || this.config.timeout,
      headers: options.headers,
    };

    try {
      const result = await withRetry(
        () => this.client.request<ApiResponseType<T>>(config),
        {
          ...this.config.retryOptions,
          ...options.retryOptions,
        }
      );

      return result.data.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Parse endpoint string into HTTP method and URL
   */
  private parseEndpoint<T extends ApiEndpoint>(
    endpoint: T,
    requestData: ApiRequest<T>
  ): {
    method: string;
    url: string;
    data?: unknown;
    params?: Record<string, unknown>;
  } {
    const [method, path] = endpoint.split(' ');
    let url = path;

    // Replace path parameters
    if (requestData && typeof requestData === 'object') {
      Object.entries(requestData).forEach(([key, value]) => {
        if (url.includes(`:${key}`)) {
          url = url.replace(`:${key}`, String(value));
        }
      });
    }

    // Extract query parameters and request body
    const params: Record<string, unknown> = {};
    const data: Record<string, unknown> = {};

    if (requestData && typeof requestData === 'object') {
      Object.entries(requestData).forEach(([key, value]) => {
        if (!url.includes(`:${key}`)) {
          if (method === 'GET') {
            params[key] = value;
          } else {
            data[key] = value;
          }
        }
      });
    }

    return {
      method: method.toLowerCase(),
      url,
      data: Object.keys(data).length > 0 ? data : undefined,
      params: Object.keys(params).length > 0 ? params : undefined,
    };
  }

  /**
   * Handle and standardize API errors
   */
  private handleError(error: unknown): Error {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      
      if (axiosError.response) {
        const { status, data } = axiosError.response;
        const errorMessage = this.extractErrorMessage(data);
        
        return new Error(
          `API Error ${status}: ${errorMessage || axiosError.message}`
        );
      } else if (axiosError.request) {
        return new Error('Network error: No response received');
      }
    }

    return error instanceof Error ? error : new Error(String(error));
  }

  /**
   * Extract error message from API response
   */
  private extractErrorMessage(data: unknown): string {
    if (typeof data === 'object' && data !== null) {
      const response = data as Record<string, unknown>;
      
      if (response.error) {
        return String(response.error);
      }
      
      if (response.message) {
        return String(response.message);
      }
      
      if (response.details && Array.isArray(response.details)) {
        const details = response.details as Array<{ message: string }>;
        return details.map(d => d.message).join(', ');
      }
    }
    
    return 'Unknown error occurred';
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<ApiResponse<{ status: string; message: string }>> {
    const response = await this.request('GET /health', {});
    // Transform the response to match the expected format
    return {
      success: response.success,
      data: {
        status: response.data?.status || 'unknown',
        message: response.data?.service || 'Health check response',
      },
      error: response.error,
      message: response.message,
    };
  }

  /**
   * System status endpoint
   */
  async systemStatus(): Promise<ApiResponse<{ message: string; status: string }>> {
    const response = await this.request('GET /', {});
    return response;
  }
}

/**
 * Default API client instance
 */
export const apiClient = new ApiClient();

/**
 * Type-safe API functions for each endpoint
 */

// Auth endpoints
export const authApi = {
  googleLogin: (request: ApiRequest<'POST /auth/google'>) =>
    apiClient.request('POST /auth/google', request),
  
  getCurrentUser: () =>
    apiClient.request('GET /auth/me', {}),
  
  logout: () =>
    apiClient.request('POST /auth/logout', {}),
  
  refreshToken: (request: ApiRequest<'POST /auth/refresh'>) =>
    apiClient.request('POST /auth/refresh', request),
};

// Project endpoints
export const projectApi = {
  getProjects: (request: ApiRequest<'GET /projects'>) =>
    apiClient.request('GET /projects', request),
  
  createProject: (request: ApiRequest<'POST /projects'>) =>
    apiClient.request('POST /projects', request),
  
  getProject: (request: ApiRequest<'GET /projects/:id'>) =>
    apiClient.request('GET /projects/:id', request),
  
  deleteProject: (request: ApiRequest<'DELETE /projects/:id'>) =>
    apiClient.request('DELETE /projects/:id', request),
  
  getUploadUrl: (request: ApiRequest<'GET /projects/:id/upload-url'>) =>
    apiClient.request('GET /projects/:id/upload-url', request),
  
  getProjectStatus: (request: ApiRequest<'GET /projects/:id/status'>) =>
    apiClient.request('GET /projects/:id/status', request),
};

// Chat endpoints
export const chatApi = {
  sendMessage: (request: ApiRequest<'POST /chat/:project_id/message'>) =>
    apiClient.request('POST /chat/:project_id/message', request),
  
  getMessages: (request: ApiRequest<'GET /chat/:project_id/messages'>) =>
    apiClient.request('GET /chat/:project_id/messages', request),
  
  getPreview: (request: ApiRequest<'GET /chat/:project_id/preview'>) =>
    apiClient.request('GET /chat/:project_id/preview', request),
  
  getSuggestions: (request: ApiRequest<'GET /chat/:project_id/suggestions'>) =>
    apiClient.request('GET /chat/:project_id/suggestions', request),
};

// System endpoints
export const systemApi = {
  healthCheck: () => apiClient.healthCheck(),
  systemStatus: () => apiClient.systemStatus(),
};

// Export all API functions
export const api = {
  auth: authApi,
  projects: projectApi,
  chat: chatApi,
  system: systemApi,
};

// Export types for convenience
export type { ApiClientConfig }; 