# Environment Setup Guide

This document describes the environment variables needed for both frontend and backend components.

## Frontend Environment Variables

Create a file `frontend/.env.local` with the following contents:

```bash
# Backend API URL - where the FastAPI server is running
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# Authentication (will be added in auth tasks)
# NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
# NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## Backend Environment Variables

Create a file `backend/.env` with the following contents:

```bash
# Server Configuration
PORT=8000
FRONTEND_URL=http://localhost:3000

# Database Configuration (will be added in Task B2)
# DATABASE_URL=postgresql://user:password@localhost:5432/smartquery
# REDIS_URL=redis://localhost:6379

# Storage Configuration (will be added in Task B2)
# MINIO_ENDPOINT=localhost:9000
# MINIO_ACCESS_KEY=your_access_key
# MINIO_SECRET_KEY=your_secret_key
# MINIO_BUCKET_NAME=smartquery-files

# AI/LLM Configuration (will be added later)
# OPENAI_API_KEY=your_openai_api_key
# LANGCHAIN_API_KEY=your_langchain_api_key

# Celery Configuration (will be added in Task B2)
# CELERY_BROKER_URL=redis://localhost:6379
# CELERY_RESULT_BACKEND=redis://localhost:6379
```

## Setup Instructions

1. **Frontend Setup:**
   ```bash
   cd frontend
   cp .env.example .env.local  # or create .env.local manually
   # Edit .env.local with your values
   ```

2. **Backend Setup:**
   ```bash
   cd backend
   cp .env.example .env  # or create .env manually
   # Edit .env with your values
   ```

## Testing Environment Variables

To test that environment variables are loading correctly:

### Frontend
- Start the development server: `npm run dev`
- The app should be able to make requests to `http://localhost:8000`

### Backend
- Start the FastAPI server: `python main.py`
- The server should start on port 8000 and accept requests from `http://localhost:3000`

## Environment Variable Validation

The applications will validate that required environment variables are set on startup and provide clear error messages if any are missing. 