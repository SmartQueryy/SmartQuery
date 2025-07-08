// SmartQuery API Contract - TypeScript Interfaces
// This file defines the complete API specification for frontend-backend communication

// ===========================================
// BASE TYPES & ENUMS
// ===========================================

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginationParams {
  page?: number;
  limit?: number;
  offset?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

// ===========================================
// AUTHENTICATION ENDPOINTS
// ===========================================

export interface User {
  id: string;
  email: string;
  name: string;
  avatar_url?: string;
  created_at: string;
  last_sign_in_at?: string;
}

export interface LoginRequest {
  google_token: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  expires_in: number;
}

// Auth API Endpoints
export interface AuthEndpoints {
  'POST /auth/google': {
    request: LoginRequest;
    response: ApiResponse<AuthResponse>;
  };
  'GET /auth/me': {
    request: {};
    response: ApiResponse<User>;
  };
  'POST /auth/logout': {
    request: {};
    response: ApiResponse<{ message: string }>;
  };
  'POST /auth/refresh': {
    request: { refresh_token: string };
    response: ApiResponse<AuthResponse>;
  };
}

// ===========================================
// PROJECT MANAGEMENT ENDPOINTS
// ===========================================

export interface Project {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  csv_filename: string;
  csv_path: string;
  row_count: number;
  column_count: number;
  columns_metadata: ColumnMetadata[];
  created_at: string;
  updated_at: string;
  status: ProjectStatus;
}

export interface ColumnMetadata {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'date' | 'datetime';
  nullable: boolean;
  sample_values: any[];
  unique_count?: number;
  min_value?: number;
  max_value?: number;
}

export type ProjectStatus = 'uploading' | 'processing' | 'ready' | 'error';

export interface CreateProjectRequest {
  name: string;
  description?: string;
}

export interface CreateProjectResponse {
  project: Project;
  upload_url: string;
  upload_fields: Record<string, string>;
}

export interface UploadStatusResponse {
  project_id: string;
  status: ProjectStatus;
  progress: number;
  message?: string;
  error?: string;
}

// Project API Endpoints
export interface ProjectEndpoints {
  'GET /projects': {
    request: PaginationParams;
    response: ApiResponse<PaginatedResponse<Project>>;
  };
  'POST /projects': {
    request: CreateProjectRequest;
    response: ApiResponse<CreateProjectResponse>;
  };
  'GET /projects/:id': {
    request: { id: string };
    response: ApiResponse<Project>;
  };
  'DELETE /projects/:id': {
    request: { id: string };
    response: ApiResponse<{ message: string }>;
  };
  'GET /projects/:id/upload-url': {
    request: { id: string };
    response: ApiResponse<{ upload_url: string; upload_fields: Record<string, string> }>;
  };
  'GET /projects/:id/status': {
    request: { id: string };
    response: ApiResponse<UploadStatusResponse>;
  };
}

// ===========================================
// CHAT & QUERY ENDPOINTS
// ===========================================

export interface ChatMessage {
  id: string;
  project_id: string;
  user_id: string;
  content: string;
  role: 'user' | 'assistant';
  created_at: string;
  metadata?: Record<string, any>;
}

export interface SendMessageRequest {
  project_id: string;
  message: string;
  context?: string[];
}

export interface QueryResult {
  id: string;
  query: string;
  sql_query?: string;
  result_type: 'table' | 'chart' | 'summary' | 'error';
  data?: any[];
  chart_config?: ChartConfig;
  summary?: string;
  error?: string;
  execution_time: number;
  row_count?: number;
}

export interface ChartConfig {
  type: 'bar' | 'line' | 'pie' | 'scatter' | 'histogram';
  x_axis: string;
  y_axis: string;
  title?: string;
  colors?: string[];
}

export interface SendMessageResponse {
  message: ChatMessage;
  result?: QueryResult;
}

export interface CSVPreview {
  columns: string[];
  sample_data: any[][];
  total_rows: number;
  data_types: Record<string, string>;
}

export interface QuerySuggestion {
  id: string;
  text: string;
  category: 'analysis' | 'visualization' | 'summary' | 'filter';
  complexity: 'beginner' | 'intermediate' | 'advanced';
}

// Chat API Endpoints
export interface ChatEndpoints {
  'POST /chat/:project_id/message': {
    request: SendMessageRequest;
    response: ApiResponse<SendMessageResponse>;
  };
  'GET /chat/:project_id/messages': {
    request: { project_id: string } & PaginationParams;
    response: ApiResponse<PaginatedResponse<ChatMessage>>;
  };
  'GET /chat/:project_id/preview': {
    request: { project_id: string };
    response: ApiResponse<CSVPreview>;
  };
  'GET /chat/:project_id/suggestions': {
    request: { project_id: string };
    response: ApiResponse<QuerySuggestion[]>;
  };
}

// ===========================================
// HEALTH & SYSTEM ENDPOINTS
// ===========================================

export interface HealthStatus {
  status: 'healthy' | 'unhealthy';
  service: string;
  version: string;
  timestamp: string;
  checks: {
    database: boolean;
    redis: boolean;
    storage: boolean;
    llm_service: boolean;
  };
}

export interface SystemEndpoints {
  'GET /health': {
    request: {};
    response: ApiResponse<HealthStatus>;
  };
  'GET /': {
    request: {};
    response: ApiResponse<{ message: string; status: string }>;
  };
}

// ===========================================
// COMPLETE API CONTRACT
// ===========================================

export type ApiContract = 
  & AuthEndpoints 
  & ProjectEndpoints 
  & ChatEndpoints 
  & SystemEndpoints;

// ===========================================
// ERROR RESPONSES
// ===========================================

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export interface ApiError {
  error: string;
  message: string;
  code: number;
  details?: ValidationError[];
  timestamp: string;
}

// Standard HTTP Status Codes
export enum HttpStatus {
  OK = 200,
  CREATED = 201,
  BAD_REQUEST = 400,
  UNAUTHORIZED = 401,
  FORBIDDEN = 403,
  NOT_FOUND = 404,
  CONFLICT = 409,
  UNPROCESSABLE_ENTITY = 422,
  INTERNAL_SERVER_ERROR = 500,
  SERVICE_UNAVAILABLE = 503
}

// ===========================================
// REQUEST HEADERS
// ===========================================

export interface RequestHeaders {
  'Content-Type': string;
  'Authorization'?: string;
  'X-API-Key'?: string;
  'X-Request-ID'?: string;
} 