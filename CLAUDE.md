# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SmartQuery is a natural language CSV querying application built as a monorepo. Users can upload CSV files and query them using natural language, which gets converted to SQL and executed via DuckDB.

**Architecture**: Next.js 14 frontend + FastAPI backend with PostgreSQL, Redis, MinIO, and Celery for background processing.

## Development Commands

### Root Commands (Turborepo)
```bash
npm run install:all    # Install all dependencies
npm run dev            # Start both frontend and backend
npm run build          # Build all projects
npm run lint           # Lint all projects
npm run test           # Test all projects
npm run clean          # Clean build artifacts
```

### Frontend Commands
```bash
cd frontend
npm run dev                # Development server
npm run build              # Production build
npm run lint               # ESLint
npm run type-check         # TypeScript checking
npm run test               # Unit tests (Vitest)
npm run test:e2e          # E2E tests (Playwright)
npm run test:integration  # Integration tests
```

### Backend Commands
```bash
cd backend
python main.py                                    # Development server
pip install -r requirements.txt                   # Install dependencies
pytest tests/                                     # All tests
pytest tests/integration/                         # Integration tests
pytest tests/performance/                         # Performance tests
celery -A celery_app worker --loglevel=info      # Start Celery worker
```

### Infrastructure
```bash
docker-compose up -d       # Start all services (PostgreSQL, Redis, MinIO, Celery)
docker-compose down        # Stop services
docker-compose logs -f     # View logs
```

## Architecture & Tech Stack

### Frontend (Next.js 14)
- **Framework**: Next.js 14 with TypeScript and App Router
- **Styling**: Tailwind CSS with DaisyUI components
- **State Management**: Zustand stores in `src/lib/store/`
- **API Client**: Centralized in `src/lib/api.ts` with retry logic
- **Charts**: Recharts for data visualization
- **Authentication**: Google OAuth with JWT tokens

### Backend (FastAPI)
- **Framework**: FastAPI with SQLAlchemy ORM
- **Database**: PostgreSQL for persistence, DuckDB for CSV query execution
- **Cache/Queue**: Redis for caching and Celery message broker
- **Storage**: MinIO (S3-compatible) for CSV files
- **AI/ML**: OpenAI GPT + LangChain for NL-to-SQL conversion, OpenAI embeddings for semantic search
- **Background Tasks**: Celery for async CSV processing

### Key Architecture Patterns

1. **Service Layer Pattern**: Business logic separated into services (`backend/services/`)
2. **Centralized API Client**: All HTTP requests go through `frontend/src/lib/api.ts`
3. **Shared API Contract**: TypeScript definitions in `shared/api-contract.ts`
4. **Async Processing**: Celery tasks for CSV analysis and long-running operations

## Project Structure

```
SmartQuery/
├── frontend/src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── dashboard/       # Protected dashboard
│   │   ├── login/           # Authentication
│   │   └── workspace/       # CSV query interface
│   ├── components/          # Reusable components
│   │   ├── auth/            # Authentication components
│   │   ├── dashboard/       # Dashboard components
│   │   └── layout/          # Layout components
│   ├── lib/
│   │   ├── api.ts           # Centralized API client
│   │   ├── types.ts         # TypeScript definitions
│   │   └── store/           # Zustand state stores
│   └── __tests__/           # Frontend tests
├── backend/
│   ├── api/                 # FastAPI route handlers
│   ├── services/            # Business logic services
│   ├── models/              # Database models & schemas
│   ├── tasks/               # Celery background tasks
│   └── tests/               # Backend tests
├── shared/
│   └── api-contract.ts      # Shared TypeScript API definitions
└── docker-compose.yml       # Development infrastructure
```

## Environment Setup

### Required Environment Files

**Frontend** (`.env.local`):
```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

**Backend** (`.env`):
```bash
PORT=8000
FRONTEND_URL=http://localhost:3000
DATABASE_URL=postgresql://smartquery_user:smartquery_dev_password@localhost:5432/smartquery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minio_admin
MINIO_SECRET_KEY=minio_dev_password123
OPENAI_API_KEY=your_openai_api_key
```

## Development Workflow

1. Start infrastructure: `docker-compose up -d`
2. Start backend: `cd backend && python main.py`
3. Start frontend: `cd frontend && npm run dev`
4. Access at http://localhost:3000 (frontend) and http://localhost:8000 (backend)

## Key API Endpoints

- **Auth**: `/auth/google`, `/auth/me`, `/auth/refresh`
- **Projects**: `/projects` (CRUD), `/projects/{id}/upload-url`, `/projects/{id}/status`
- **Chat**: `/chat/{project_id}/message`, `/chat/{project_id}/messages`, `/chat/{project_id}/suggestions`
- **System**: `/health`

## Testing

- **Frontend**: Vitest for units, Playwright for E2E, both with comprehensive integration tests
- **Backend**: 125+ pytest tests covering units, integrations, and performance
- **API Contract**: Shared TypeScript definitions ensure frontend-backend compatibility

## Special Considerations

- **Semantic Search**: Uses OpenAI embeddings for intelligent query suggestions
- **Background Processing**: CSV uploads trigger async Celery tasks for schema analysis
- **Error Handling**: Centralized error handling in API client with retry logic
- **Security**: Enterprise-grade middleware with rate limiting and input validation
- **Performance**: Built-in monitoring for API endpoints and database operations