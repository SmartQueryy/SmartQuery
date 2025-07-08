import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="SmartQuery API",
    description="Backend API for SmartQuery MVP - Natural language CSV querying",
    version="1.0.0",
)

# Configure CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js development server
        "https://localhost:3000",  # HTTPS development
        os.getenv("FRONTEND_URL", "http://localhost:3000"),  # Production frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "success": True,
        "data": {"message": "SmartQuery API is running", "status": "healthy"},
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    from datetime import datetime

    return {
        "success": True,
        "data": {
            "status": "healthy",
            "service": "SmartQuery API",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "checks": {
                "database": False,  # Will be implemented in Task B2
                "redis": False,  # Will be implemented in Task B2
                "storage": False,  # Will be implemented in Task B2
                "llm_service": False,  # Will be implemented in Task B15
            },
        },
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
