import os
from dotenv import load_dotenv
from fastapi import FastAPI

from api.health import router as health_router
from api.middleware.cors import setup_cors

# Load environment variables
load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="SmartQuery API",
    description="Backend API for SmartQuery MVP - Natural language CSV querying",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup CORS middleware
setup_cors(app)

# Include routers
app.include_router(health_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "success": True,
        "data": {"message": "SmartQuery API is running", "status": "healthy"},
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Starting SmartQuery API on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
