# SmartQuery API Specification

Version: 1.0.0  
Base URL: `http://localhost:8000` (development)  
Content-Type: `application/json`

## Overview

This document describes the complete REST API for SmartQuery MVP - a natural language CSV querying platform. The API enables users to upload CSV files, manage projects, and query data using natural language.

## Authentication

All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

## Response Format

All API responses follow a consistent format:

```json
{
  "success": true,
  "data": <response_data>,
  "error": null,
  "message": "Optional message"
}
```

Error responses:
```json
{
  "success": false,
  "error": "Error description",
  "message": "User-friendly error message",
  "code": 400
}
```

## Endpoints

### Authentication

#### POST /auth/google
Authenticate user with Google OAuth token.

**Request:**
```json
{
  "google_token": "string"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "name": "John Doe",
      "avatar_url": "https://...",
      "created_at": "2025-01-01T00:00:00Z"
    },
    "access_token": "jwt_token",
    "refresh_token": "refresh_token", 
    "expires_in": 3600
  }
}
```

#### GET /auth/me
Get current user information.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "avatar_url": "https://...",
    "created_at": "2025-01-01T00:00:00Z"
  }
}
```

#### POST /auth/logout
Logout current user.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Logged out successfully"
  }
}
```

#### POST /auth/refresh
Refresh access token.

**Request:**
```json
{
  "refresh_token": "refresh_token"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "new_jwt_token",
    "expires_in": 3600
  }
}
```

### Projects

#### GET /projects
List user's projects with pagination.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "uuid",
        "user_id": "uuid",
        "name": "Sales Data Analysis",
        "description": "Monthly sales data",
        "csv_filename": "sales_data.csv",
        "csv_path": "user_id/project_id/sales_data.csv",
        "row_count": 1000,
        "column_count": 8,
        "columns_metadata": [
          {
            "name": "date",
            "type": "date",
            "nullable": false,
            "sample_values": ["2025-01-01", "2025-01-02"],
            "unique_count": 365
          }
        ],
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
        "status": "ready"
      }
    ],
    "total": 1,
    "page": 1,
    "limit": 20,
    "hasMore": false
  }
}
```

#### POST /projects
Create new project.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "name": "Project Name",
  "description": "Optional description"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "project": {
      "id": "uuid",
      "user_id": "uuid",
      "name": "Project Name",
      "status": "uploading",
      "created_at": "2025-01-01T00:00:00Z"
    },
    "upload_url": "https://storage.example.com/upload",
    "upload_fields": {
      "key": "user_id/project_id/filename",
      "policy": "base64_policy",
      "signature": "signature"
    }
  }
}
```

#### GET /projects/:id
Get project details.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Project Name",
    "status": "ready",
    "row_count": 1000,
    "column_count": 8,
    "columns_metadata": [...]
  }
}
```

#### DELETE /projects/:id
Delete project.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Project deleted successfully"
  }
}
```

#### GET /projects/:id/upload-url
Get presigned URL for file upload.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "data": {
    "upload_url": "https://storage.example.com/upload",
    "upload_fields": {
      "key": "user_id/project_id/filename",
      "policy": "base64_policy"
    }
  }
}
```

#### GET /projects/:id/status
Get project processing status.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "data": {
    "project_id": "uuid",
    "status": "processing",
    "progress": 75,
    "message": "Analyzing CSV schema..."
  }
}
```

### Chat & Queries

#### POST /chat/:project_id/message
Send message and get query results.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "message": "Show me the top 5 products by sales",
  "context": ["previous_query_id"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message": {
      "id": "uuid",
      "project_id": "uuid",
      "user_id": "uuid",
      "content": "Show me the top 5 products by sales",
      "role": "user",
      "created_at": "2025-01-01T00:00:00Z"
    },
    "result": {
      "id": "uuid",
      "query": "Show me the top 5 products by sales",
      "sql_query": "SELECT product_name, SUM(sales) as total_sales FROM data GROUP BY product_name ORDER BY total_sales DESC LIMIT 5",
      "result_type": "table",
      "data": [
        {"product_name": "Product A", "total_sales": 50000},
        {"product_name": "Product B", "total_sales": 45000}
      ],
      "execution_time": 0.5,
      "row_count": 5
    }
  }
}
```

#### GET /chat/:project_id/messages
Get chat message history.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page` (optional): Page number
- `limit` (optional): Messages per page

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "uuid",
        "content": "Show me sales data",
        "role": "user",
        "created_at": "2025-01-01T00:00:00Z"
      }
    ],
    "total": 10,
    "page": 1,
    "limit": 20,
    "hasMore": false
  }
}
```

#### GET /chat/:project_id/preview
Get CSV data preview.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "data": {
    "columns": ["date", "product", "sales", "quantity"],
    "sample_data": [
      ["2025-01-01", "Product A", 1000, 10],
      ["2025-01-02", "Product B", 1500, 15]
    ],
    "total_rows": 1000,
    "data_types": {
      "date": "date",
      "product": "string",
      "sales": "number",
      "quantity": "number"
    }
  }
}
```

#### GET /chat/:project_id/suggestions
Get query suggestions.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "text": "Show me total sales by month",
      "category": "analysis",
      "complexity": "beginner"
    },
    {
      "id": "uuid", 
      "text": "Create a bar chart of top products",
      "category": "visualization",
      "complexity": "intermediate"
    }
  ]
}
```

### System

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "SmartQuery API",
    "version": "1.0.0",
    "timestamp": "2025-01-01T00:00:00Z",
    "checks": {
      "database": true,
      "redis": true,
      "storage": true,
      "llm_service": true
    }
  }
}
```

#### GET /
Root endpoint.

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "SmartQuery API is running",
    "status": "healthy"
  }
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid request data |
| 401 | Unauthorized - Invalid or missing token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource already exists |
| 422 | Unprocessable Entity - Validation errors |
| 500 | Internal Server Error - Server error |
| 503 | Service Unavailable - Service temporarily unavailable |

## Rate Limiting

- Authentication endpoints: 10 requests per minute
- Project endpoints: 100 requests per minute  
- Chat endpoints: 20 requests per minute
- System endpoints: No limit

## WebSocket Support (Future)

Real-time updates for:
- File processing status
- Query execution progress
- Live chat responses

## Frontend Integration

The API is designed to work with the central API client pattern:

```typescript
// Example usage in frontend
const api = {
  auth: {
    loginWithGoogle: (token: string) => post('/auth/google', { google_token: token }),
    getMe: () => get('/auth/me'),
    logout: () => post('/auth/logout'),
  },
  projects: {
    list: (params?: PaginationParams) => get('/projects', params),
    create: (data: CreateProjectRequest) => post('/projects', data),
    get: (id: string) => get(`/projects/${id}`),
    delete: (id: string) => del(`/projects/${id}`),
  },
  chat: {
    sendMessage: (projectId: string, message: string) => 
      post(`/chat/${projectId}/message`, { message }),
    getPreview: (projectId: string) => get(`/chat/${projectId}/preview`),
    getSuggestions: (projectId: string) => get(`/chat/${projectId}/suggestions`),
  }
};
```

This API specification ensures consistent communication between the frontend and backend throughout the development process. 