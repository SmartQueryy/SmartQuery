import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app: FastAPI) -> None:
    """Configure CORS middleware for the FastAPI application"""

    # Get allowed origins from environment
    allowed_origins = [
        "http://localhost:3000",  # Next.js development server
        "https://localhost:3000",  # HTTPS development
        os.getenv("FRONTEND_URL", "http://localhost:3000"),  # Production frontend URL
    ]

    # Add additional origins from environment variable if specified
    additional_origins = os.getenv("ADDITIONAL_CORS_ORIGINS", "")
    if additional_origins:
        allowed_origins.extend(additional_origins.split(","))

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
