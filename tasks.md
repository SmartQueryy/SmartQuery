SmartQuery MVP - Parallel Development with Central API Client
🎯 Updated Development Strategy

Person A: Frontend with centralized API client
Person B: Backend endpoints with mock support
Integration: Central lib/api.ts file manages all backend communication
Mocking: Frontend can work with mocked endpoints while backend develops real ones


📋 Phase 0: Project Bootstrap (Tasks 1-10)
🤝 Shared Setup (Tasks 1-4)
Task 1: Initialize Monorepo Structure

What: Create monorepo with Turborepo and directory structure
Start: Empty repository
End: Monorepo with /frontend, /backend, /infra, /docs directories
Test: Can run commands from root, directories exist with basic structure
Files: package.json, turbo.json, directory structure

Task 2: Setup Environment Configuration

What: Create environment variables for API communication
Start: Monorepo structure exists
End: Environment templates with backend URL configuration
Test: Environment variables load correctly in both projects
Files: frontend/.env.local, backend/.env, shared/env.example

Task 3: Define API Contract Specifications

What: Document all API endpoints, request/response schemas
Start: Environment config exists
End: Complete API specification with TypeScript interfaces
Test: API contract is comprehensive and matches both frontend/backend needs
Files: shared/api-contract.ts, docs/API_SPEC.md

Task 4: Setup CI/CD Pipeline

What: GitHub Actions for linting, testing, and deployment
Start: API contract defined
End: CI pipeline that tests both frontend and backend
Test: GitHub Actions run on PR, lint/test both projects
Files: .github/workflows/ci.yml

👤 Person A: Frontend Foundation (Tasks A1-A3)
Task A1: Initialize Next.js Project with Dependencies

What: Scaffold Next.js 14 with TypeScript, Tailwind, daisyUI, Zustand, Recharts
Start: Monorepo structure exists
End: Next.js project with all dependencies configured
Test: npm run dev starts app, all libraries importable
Files: frontend/package.json, frontend/next.config.js, frontend/tailwind.config.js

Task A2: Create Central API Client

What: Build central lib/api.ts file for all backend communication
Start: Next.js project scaffolded
End: API client with environment-based URL and TypeScript types
Test: API client configured, can make requests to backend URL
Files: frontend/src/lib/api.ts, frontend/src/types/api.ts

Task A3: Setup Environment Variables

What: Configure NEXT_PUBLIC_BACKEND_URL and other environment variables
Start: API client created
End: Environment variables properly configured and typed
Test: Backend URL loads from environment, fallbacks work for development
Files: frontend/.env.local, frontend/.env.example, frontend/src/lib/env.ts

⚙️ Person B: Backend Foundation (Tasks B1-B3)
Task B1: Initialize FastAPI Project

What: Scaffold FastAPI project with proper structure and CORS
Start: Monorepo structure exists
End: FastAPI app responding to frontend requests
Test: FastAPI accepts requests from frontend URL, CORS configured
Files: backend/main.py, backend/requirements.txt

Task B2: Setup Infrastructure with Docker

What: Configure PostgreSQL, Redis, MinIO, and Celery with Docker
Start: FastAPI project exists
End: Docker Compose with all backend services running
Test: All services start and connect, FastAPI can communicate with each
Files: docker-compose.yml, service configuration files

Task B3: Create Mock Endpoint Responses

What: Create mock endpoints that match the API contract
Start: Infrastructure running
End: Mock endpoints returning proper response structures
Test: Frontend can call all documented endpoints and receive valid responses
Files: backend/api/mock_endpoints.py


📋 Phase 1: Authentication System (Tasks 11-20)
👤 Person A: Frontend Auth (Tasks A4-A8)
Task A4: Add Auth Endpoints to API Client

What: Add authentication methods to central API client
Start: Central API client exists
End: API client with auth methods (login, register, me, logout)
Test: Can call auth endpoints, handle tokens, manage auth state
Files: Updated frontend/src/lib/api.ts

typescript// Example API client structure
export const api = {
  auth: {
    loginWithGoogle: () => apiClient.post('/auth/google'),
    getMe: () => apiClient.get('/auth/me'),
    logout: () => apiClient.post('/auth/logout'),
  },
  // ... other endpoints
}
Task A5: Setup NextAuth with API Integration

What: Configure NextAuth.js to work with backend API via api client
Start: Auth endpoints in API client
End: NextAuth using central API client for user management
Test: Google OAuth works, user data synced with backend via API client
Files: frontend/src/app/api/auth/[...nextauth]/route.ts, auth configuration

Task A6: Create Auth UI Components

What: Build hero section, login button, and auth wrapper using API client
Start: NextAuth configured
End: Complete auth UI integrated with central API client
Test: UI components trigger API calls through central client
Files: frontend/src/components/auth/, UI components

Task A7: Build Auth State Management

What: Zustand store for auth state integrated with API client
Start: Auth UI exists
End: Auth state management using central API client
Test: Auth state updates when API calls succeed/fail
Files: frontend/src/stores/auth-store.ts

Task A8: Test Frontend Auth Flow

What: End-to-end auth testing with mocked backend responses
Start: Auth state management complete
End: Complete auth flow working with mocked API responses
Test: Can login, access protected routes, logout - all via API client
Files: Test documentation and validation

⚙️ Person B: Backend Auth Implementation (Tasks B4-B8)
Task B4: Create User Model and Database

What: Define User model and create PostgreSQL table
Start: Infrastructure running
End: User table with proper schema and relationships
Test: Can create user records, constraints work correctly
Files: backend/models/user.py, database migration files

Task B5: Implement Auth Endpoints

What: Replace mock auth endpoints with real implementation
Start: User model exists
End: Working auth endpoints that match API contract exactly
Test: All auth endpoints work, responses match frontend expectations
Files: backend/api/auth.py

Task B6: Add JWT Token Management

What: Implement JWT generation, validation, and refresh
Start: Auth endpoints implemented
End: Complete JWT system with proper security
Test: Tokens generate/validate correctly, refresh mechanism works
Files: backend/services/auth_service.py, backend/middleware/auth.py

Task B7: Integrate Google OAuth Validation

What: Validate Google OAuth tokens and sync user data
Start: JWT system working
End: Google OAuth integration storing user data properly
Test: Google login creates/updates users, token validation works
Files: Updated backend/api/auth.py

Task B8: Test Backend Auth Integration

What: Verify backend auth works with frontend API client
Start: Google OAuth integrated
End: Frontend-backend auth integration fully functional
Test: Frontend can authenticate users through real backend endpoints
Files: Integration test documentation


📋 Phase 2: Dashboard & Project Management (Tasks 21-32)
👤 Person A: Dashboard with API Client (Tasks A9-A14)
Task A9: Add Project Endpoints to API Client

What: Add project management methods to central API client
Start: Auth working with API client
End: API client with all project-related methods
Test: Can call project endpoints, handle responses and errors
Files: Updated frontend/src/lib/api.ts

typescript// Extended API client
export const api = {
  // ... auth methods
  projects: {
    list: () => apiClient.get('/projects'),
    create: (data: CreateProjectRequest) => apiClient.post('/projects', data),
    getUploadUrl: (projectId: string) => apiClient.get(`/projects/${projectId}/upload-url`),
    getStatus: (projectId: string) => apiClient.get(`/projects/${projectId}/status`),
  }
}
Task A10: Build Dashboard Page with API Integration

What: Create dashboard page using API client for project data
Start: Project endpoints in API client
End: Dashboard displaying projects from API with loading states
Test: Dashboard loads projects via API client, handles loading/error states
Files: frontend/src/app/dashboard/page.tsx

Task A11: Create Project Management Components

What: Build project tiles, new project button, and modal using API client
Start: Dashboard page exists
End: Complete project management UI using central API client
Test: Can create projects, view project list, all through API client
Files: frontend/src/components/dashboard/

Task A12: Implement File Upload Flow

What: File upload using API client for presigned URLs and status updates
Start: Project components exist
End: Complete file upload flow through API client
Test: Can upload files, track progress, handle errors via API client
Files: frontend/src/services/upload-service.ts

Task A13: Add Project State Management

What: Zustand store for project data integrated with API client
Start: File upload working
End: Project state management using API client responses
Test: Project state updates correctly based on API responses
Files: frontend/src/stores/project-store.ts

Task A14: Test Dashboard with Mocked Data

What: Comprehensive testing of dashboard with mocked API responses
Start: Project state management complete
End: Dashboard fully functional with mocked backend
Test: All dashboard features work with realistic mock data
Files: Test validation and mock data documentation

⚙️ Person B: Project Backend Implementation (Tasks B9-B14)
Task B9: Create Project Model and Database

What: Define Project model with PostgreSQL table
Start: Auth backend complete
End: Project table with proper relationships to users
Test: Can create project records, foreign keys work correctly
Files: backend/models/project.py, database migrations

Task B10: Implement Project CRUD Endpoints

What: Replace mock project endpoints with real implementation
Start: Project model exists
End: Working project endpoints matching API contract
Test: All project endpoints work, responses match frontend expectations
Files: backend/api/projects.py

Task B11: Setup MinIO Integration

What: MinIO integration for file storage with presigned URLs
Start: Project endpoints working
End: File upload system with MinIO storage
Test: Can generate presigned URLs, files upload successfully to MinIO
Files: backend/services/storage_service.py

Task B12: Create Celery File Processing

What: Background task to process uploaded CSV files
Start: MinIO integration working
End: Celery task processing CSV files and updating project status
Test: Files processed asynchronously, status updates correctly
Files: backend/tasks/file_processing.py

Task B13: Add Schema Analysis

What: Analyze CSV schema and store metadata
Start: File processing working
End: Schema analysis storing column info and data types
Test: Schema metadata stored and retrievable via API
Files: Updated backend/tasks/file_processing.py

Task B14: Test Project Integration

What: Verify project system works with frontend API client
Start: Schema analysis complete
End: Complete project management working frontend-to-backend
Test: Frontend can create, upload, and track projects through real backend
Files: Integration test documentation


📋 Phase 3: Chat Interface & Workspace (Tasks 33-44)
👤 Person A: Chat Frontend with API Client (Tasks A15-A20)
Task A15: Add Chat Endpoints to API Client

What: Add chat and workspace methods to central API client
Start: Project management working
End: API client with chat, preview, and query methods
Test: Can call chat endpoints, handle real-time-like responses
Files: Updated frontend/src/lib/api.ts

typescript// Further extended API client
export const api = {
  // ... previous methods
  chat: {
    sendMessage: (projectId: string, message: string) => 
      apiClient.post(`/chat/${projectId}/message`, { message }),
    getPreview: (projectId: string) => apiClient.get(`/chat/${projectId}/preview`),
    getSuggestions: (projectId: string) => apiClient.get(`/chat/${projectId}/suggestions`),
  }
}
Task A16: Build Chat Page Layout

What: Create 3-pane chat interface with API client integration
Start: Chat endpoints in API client
End: Chat page layout loading data via API client
Test: Chat page loads project data and preview via API client
Files: frontend/src/app/chat/[projectId]/page.tsx

Task A17: Create Chat Interface Components

What: Chat messages, input, and send functionality using API client
Start: Chat layout exists
End: Interactive chat interface using central API client
Test: Can send messages and receive responses via API client
Files: frontend/src/components/chat/

Task A18: Build CSV Preview Panel

What: CSV preview panel using API client for data
Start: Chat interface working
End: CSV preview displaying data from API client
Test: Preview loads CSV data via API client, displays correctly
Files: frontend/src/components/workspace/csv-preview.tsx

Task A19: Create Results Display Panel

What: Query results panel handling different response types from API
Start: CSV preview working
End: Results panel displaying API responses (tables, charts, text)
Test: Can display different result types from API responses
Files: frontend/src/components/workspace/results-panel.tsx

Task A20: Add Chat State Management

What: Zustand store for chat state using API client
Start: Results panel complete
End: Chat state management integrated with API client
Test: Chat state updates correctly based on API responses
Files: frontend/src/stores/chat-store.ts

⚙️ Person B: Chat Backend Implementation (Tasks B15-B20)
Task B15: Setup LangChain Integration

What: Configure LangChain for query processing
Start: Project system complete
End: LangChain agent for SQL and semantic search decisions
Test: LangChain makes appropriate query routing decisions
Files: backend/services/langchain_service.py

Task B16: Implement Chat Message Endpoint

What: Replace mock chat endpoint with LangChain integration
Start: LangChain configured
End: Chat endpoint processing messages and returning results
Test: Chat endpoint accepts messages, returns properly formatted responses
Files: backend/api/chat.py

Task B17: Add DuckDB Query Execution

What: SQL query execution on DuckDB with result formatting
Start: Chat endpoint working
End: SQL queries executing on CSV data, results formatted for frontend
Test: SQL queries return properly formatted results matching API contract
Files: backend/services/duckdb_service.py

Task B18: Create CSV Preview Endpoint

What: Endpoint returning CSV preview data
Start: DuckDB queries working
End: Preview endpoint returning formatted CSV sample data
Test: Preview endpoint returns data matching frontend expectations
Files: Updated backend/api/chat.py

Task B19: Setup Embeddings System

What: OpenAI embeddings for semantic search
Start: Preview endpoint working
End: Embedding generation and storage for semantic queries
Test: Can generate embeddings and perform semantic search
Files: backend/services/embeddings_service.py

Task B20: Create Query Suggestions

What: Generate intelligent query suggestions
Start: Embeddings working
End: Suggestions endpoint returning relevant queries
Test: Suggestions are relevant and useful for the dataset
Files: backend/services/suggestions_service.py


📋 Phase 4: Visualization & Analytics (Tasks 45-52)
👤 Person A: Visualization with API Client (Tasks A21-A24)
Task A21: Integrate Recharts with API Responses

What: Render charts based on API response data structures
Start: Chat system working
End: Charts rendering data from API client responses
Test: Different chart types render correctly from API data
Files: frontend/src/components/charts/

Task A22: Handle Multiple Result Types

What: Display tables, charts, summaries based on API response type
Start: Charts integrated
End: Results panel adapting to API response result_type field
Test: All result types from API display correctly
Files: Updated frontend/src/components/workspace/results-panel.tsx

Task A23: Add Query Suggestions UI

What: Interactive suggestions using API client suggestions endpoint
Start: Result types working
End: Suggestion bar integrated with API client
Test: Suggestions load from API, clicking populates input
Files: frontend/src/components/chat/suggestions-bar.tsx

Task A24: Improve UI/UX and Responsiveness

What: Polish UI, add dark mode, smooth transitions
Start: Suggestions working
End: Professional UI with responsive design
Test: App works well on all devices, smooth user experience
Files: CSS/styling files, theme configuration

⚙️ Person B: Analytics Backend (Tasks B21-B24)
Task B21: Enhance Query Processing

What: Improve LangChain query routing and SQL generation
Start: Basic chat working
End: More sophisticated query processing with better accuracy
Test: Complex queries processed correctly, appropriate routing decisions
Files: Updated backend/services/langchain_service.py

Task B22: Optimize Vector Search

What: Improve embeddings storage and semantic search performance
Start: Basic embeddings working
End: Optimized vector search with better relevance
Test: Semantic search returns more relevant results faster
Files: Updated backend/services/embeddings_service.py

Task B23: Add Performance Monitoring

What: Monitor API response times and query performance
Start: Vector search optimized
End: Performance metrics for all endpoints
Test: Can track API performance, identify bottlenecks
Files: backend/middleware/monitoring.py

Task B24: Standardize API Response Format

What: Ensure all endpoints return consistent response structure
Start: Performance monitoring added
End: Consistent API response format across all endpoints
Test: All API responses match the documented contract structure
Files: backend/models/response_schemas.py


📋 Phase 5: Testing & Polish (Tasks 53-60)
👤 Person A: Frontend Testing (Tasks A25-A28)
Task A25: Write API Client Tests

What: Unit tests for the central API client
Start: Application features complete
End: Comprehensive tests for all API client methods
Test: API client tests pass, error handling covered
Files: frontend/src/lib/__tests__/api.test.ts

Task A26: Component Integration Tests

What: Test components with mocked API client responses
Start: API client tests complete
End: Component tests using mocked API responses
Test: Components handle all API response scenarios correctly
Files: frontend/src/components/__tests__/

Task A27: End-to-End Testing

What: E2E tests using real API endpoints
Start: Component tests complete
End: Complete user journey tested with real backend
Test: E2E tests pass with real API integration
Files: frontend/e2e/, Playwright configuration

Task A28: Error Handling and Edge Cases

What: Comprehensive error handling for all API scenarios
Start: E2E tests complete
End: Robust error handling throughout the application
Test: App handles all API error scenarios gracefully
Files: Error handling utilities, user feedback components

⚙️ Person B: Backend Testing (Tasks B25-B28)
Task B25: API Contract Validation

What: Ensure all endpoints match the documented API contract
Start: All features implemented
End: API contract compliance verified
Test: All endpoints return responses matching documented schemas
Files: API contract validation tests

Task B26: Integration Testing

What: Test full integration between all backend services
Start: API contract validated
End: Complete backend integration test suite
Test: All services work together correctly
Files: backend/tests/integration/

Task B27: Performance Testing

What: Load testing and performance optimization
Start: Integration tests complete
End: Performance benchmarks and optimizations
Test: API meets performance requirements under load
Files: Performance test scripts, optimization documentation

Task B28: Security and Error Handling

What: Security audit and comprehensive error handling
Start: Performance testing complete
End: Secure API with proper error responses
Test: Security scan passes, all error scenarios handled
