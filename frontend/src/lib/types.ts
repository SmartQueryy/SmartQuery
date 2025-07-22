/**
 * Type Definitions
 * 
 * Centralized TypeScript interfaces and types for the SmartQuery application.
 * These types match the API contract and provide type safety across the frontend.
 */

// ===========================================
// BASE TYPES & ENUMS
// ===========================================

export interface ApiResponse<T = unknown> {
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
  SERVICE_UNAVAILABLE = 503,
}

export interface RequestHeaders {
  'Content-Type': string;
  'Authorization'?: string;
  'X-API-Key'?: string;
  'X-Request-ID'?: string;
}

// ===========================================
// AUTHENTICATION TYPES
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

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface LogoutResponse {
  message: string;
}

// ===========================================
// PROJECT MANAGEMENT TYPES
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
  sample_values: unknown[];
  unique_count?: number;
  min_value?: number;
  max_value?: number;
  mean_value?: number;
  median_value?: number;
  std_deviation?: number;
  null_count?: number;
  null_percentage?: number;
  data_quality_issues?: string[];
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

export interface UploadUrlResponse {
  upload_url: string;
  upload_fields: Record<string, string>;
}

// ===========================================
// CHAT & QUERY TYPES
// ===========================================

export interface ChatMessage {
  id: string;
  project_id: string;
  user_id: string;
  content: string;
  role: 'user' | 'assistant';
  created_at: string;
  metadata?: Record<string, unknown>;
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
  data?: unknown[];
  chart_config?: ChartConfig;
  summary?: string;
  error?: string;
  execution_time: number;
  row_count?: number;
  title?: string;
}

export interface ChartConfig {
  type: 'bar' | 'line' | 'pie' | 'scatter' | 'histogram';
  x_axis: string;
  y_axis: string;
  title?: string;
  colors?: string[];
  options?: Record<string, unknown>;
}

export interface SendMessageResponse {
  message: ChatMessage;
  result?: QueryResult;
}

export interface CSVPreview {
  columns: string[];
  sample_data: unknown[][];
  total_rows: number;
  data_types: Record<string, string>;
}

export interface QuerySuggestion {
  id: string;
  text: string;
  category: 'analysis' | 'visualization' | 'summary' | 'filter';
  complexity: 'beginner' | 'intermediate' | 'advanced';
}

// ===========================================
// HEALTH & SYSTEM TYPES
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

export interface SystemStatus {
  message: string;
  status: string;
}

// ===========================================
// API ENDPOINT TYPES
// ===========================================

// Auth Endpoints
export interface AuthEndpoints {
  'POST /auth/google': {
    request: LoginRequest;
    response: ApiResponse<AuthResponse>;
  };
  'GET /auth/me': {
    request: Record<string, never>;
    response: ApiResponse<User>;
  };
  'POST /auth/logout': {
    request: Record<string, never>;
    response: ApiResponse<LogoutResponse>;
  };
  'POST /auth/refresh': {
    request: RefreshTokenRequest;
    response: ApiResponse<AuthResponse>;
  };
}

// Project Endpoints
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
    response: ApiResponse<LogoutResponse>;
  };
  'GET /projects/:id/upload-url': {
    request: { id: string };
    response: ApiResponse<UploadUrlResponse>;
  };
  'GET /projects/:id/status': {
    request: { id: string };
    response: ApiResponse<UploadStatusResponse>;
  };
}

// Chat Endpoints
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

// System Endpoints
export interface SystemEndpoints {
  'GET /health': {
    request: Record<string, never>;
    response: ApiResponse<HealthStatus>;
  };
  'GET /': {
    request: Record<string, never>;
    response: ApiResponse<SystemStatus>;
  };
}

// Combined API Contract
export type ApiContract = AuthEndpoints & ProjectEndpoints & ChatEndpoints & SystemEndpoints;

// ===========================================
// FRONTEND-SPECIFIC TYPES
// ===========================================

export interface LoadingState {
  isLoading: boolean;
  error: string | null;
}

export interface PaginationState {
  page: number;
  limit: number;
  total: number;
  hasMore: boolean;
}

export interface ChartDataPoint {
  name: string;
  value: number;
  [key: string]: unknown;
}

export interface ChartData {
  data: ChartDataPoint[];
  config: ChartConfig;
}

export interface FileUploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export interface SearchFilters {
  query?: string;
  status?: ProjectStatus;
  dateRange?: {
    start: Date;
    end: Date;
  };
  sortBy?: 'name' | 'created_at' | 'updated_at';
  sortOrder?: 'asc' | 'desc';
}

// ===========================================
// UTILITY TYPES
// ===========================================

export type ApiEndpoint = keyof ApiContract;

export type ApiRequest<T extends ApiEndpoint> = ApiContract[T]['request'];
export type ApiResponseType<T extends ApiEndpoint> = ApiContract[T]['response'];

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type NonNullableFields<T> = {
  [P in keyof T]: NonNullable<T[P]>;
}; 