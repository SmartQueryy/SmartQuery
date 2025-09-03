import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { 
  ApiResponse, 
  User, 
  LoginRequest, 
  AuthResponse, 
  Project, 
  CreateProjectRequest, 
  CreateProjectResponse, 
  UploadStatusResponse, 
  PaginationParams, 
  PaginatedResponse,
  SendMessageRequest,
  SendMessageResponse,
  CSVPreview,
  QuerySuggestion,
  ChatMessage,
  HealthStatus
} from '../../../shared/api-contract';

const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;
  private accessToken: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    this.client.interceptors.request.use((config) => {
      if (this.accessToken) {
        config.headers.Authorization = `Bearer ${this.accessToken}`;
      }
      return config;
    });

    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401 && this.accessToken) {
          this.accessToken = null;
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
        return Promise.reject(error);
      }
    );
  }

  setAccessToken(token: string | null) {
    this.accessToken = token;
    if (token) {
      localStorage.setItem('access_token', token);
    } else {
      localStorage.removeItem('access_token');
    }
  }

  async request<T>(config: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.request(config);
      return response.data;
    } catch (error: any) {
      if (error.response?.data) {
        return error.response.data;
      }
      return {
        success: false,
        error: error.message || 'Network error occurred',
      };
    }
  }
}

const apiClient = new ApiClient();

export const api = {
  auth: {
    googleLogin: async (data: LoginRequest): Promise<ApiResponse<AuthResponse>> => {
      return apiClient.request({
        method: 'POST',
        url: '/auth/google',
        data,
      });
    },
    getCurrentUser: async (): Promise<ApiResponse<User>> => {
      return apiClient.request({
        method: 'GET',
        url: '/auth/me',
      });
    },
    logout: async (): Promise<ApiResponse<{ message: string }>> => {
      return apiClient.request({
        method: 'POST',
        url: '/auth/logout',
      });
    },
    refreshToken: async (refresh_token: string): Promise<ApiResponse<AuthResponse>> => {
      return apiClient.request({
        method: 'POST',
        url: '/auth/refresh',
        data: { refresh_token },
      });
    },
  },
  projects: {
    getProjects: async (params?: PaginationParams): Promise<ApiResponse<PaginatedResponse<Project>>> => {
      return apiClient.request({
        method: 'GET',
        url: '/projects',
        params,
      });
    },
    createProject: async (data: CreateProjectRequest): Promise<ApiResponse<CreateProjectResponse>> => {
      return apiClient.request({
        method: 'POST',
        url: '/projects',
        data,
      });
    },
    getProject: async (id: string): Promise<ApiResponse<Project>> => {
      return apiClient.request({
        method: 'GET',
        url: `/projects/${id}`,
      });
    },
    deleteProject: async (id: string): Promise<ApiResponse<{ message: string }>> => {
      return apiClient.request({
        method: 'DELETE',
        url: `/projects/${id}`,
      });
    },
    getUploadUrl: async (projectId: string): Promise<ApiResponse<{ upload_url: string; upload_fields: Record<string, string> }>> => {
      return apiClient.request({
        method: 'GET',
        url: `/projects/${projectId}/upload-url`,
      });
    },
    getProjectStatus: async (projectId: string): Promise<ApiResponse<UploadStatusResponse>> => {
      return apiClient.request({
        method: 'GET',
        url: `/projects/${projectId}/status`,
      });
    },
  },
  chat: {
    sendMessage: async (projectId: string, message: string, context?: string[]): Promise<ApiResponse<SendMessageResponse>> => {
      return apiClient.request({
        method: 'POST',
        url: `/chat/${projectId}/message`,
        data: { project_id: projectId, message, context },
      });
    },
    getMessages: async (projectId: string, params?: PaginationParams): Promise<ApiResponse<PaginatedResponse<ChatMessage>>> => {
      return apiClient.request({
        method: 'GET',
        url: `/chat/${projectId}/messages`,
        params,
      });
    },
    getPreview: async (projectId: string): Promise<ApiResponse<CSVPreview>> => {
      return apiClient.request({
        method: 'GET',
        url: `/chat/${projectId}/preview`,
      });
    },
    getSuggestions: async (projectId: string): Promise<ApiResponse<QuerySuggestion[]>> => {
      return apiClient.request({
        method: 'GET',
        url: `/chat/${projectId}/suggestions`,
      });
    },
  },
  system: {
    healthCheck: async (): Promise<ApiResponse<HealthStatus>> => {
      return apiClient.request({
        method: 'GET',
        url: '/health',
      });
    },
    systemStatus: async (): Promise<ApiResponse<{ message: string; status: string }>> => {
      return apiClient.request({
        method: 'GET',
        url: '/',
      });
    },
  },
};

// Export individual API modules for backward compatibility
export const authApi = api.auth;
export const projectApi = api.projects;
export const chatApi = api.chat;
export const systemApi = api.system;

// Export the API client instance for token management
export { apiClient }; 