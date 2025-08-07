import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)


def setup_cors(app: FastAPI) -> None:
    """Configure secure CORS middleware for the FastAPI application"""

    environment = os.getenv("ENVIRONMENT", "development")
    is_production = environment == "production"

    # Get allowed origins from environment with security considerations
    allowed_origins = []

    if not is_production:
        # Development origins
        allowed_origins.extend(
            [
                "http://localhost:3000",  # Next.js development server
                "http://127.0.0.1:3000",  # Alternative localhost
                "https://localhost:3000",  # HTTPS development
                "https://127.0.0.1:3000",  # HTTPS alternative localhost
            ]
        )

    # Add production frontend URL
    frontend_url = os.getenv("FRONTEND_URL")
    if frontend_url:
        allowed_origins.append(frontend_url)
        # Also add HTTPS version if HTTP is provided
        if frontend_url.startswith("http://"):
            allowed_origins.append(frontend_url.replace("http://", "https://"))

    # Add additional origins from environment variable if specified
    additional_origins = os.getenv("ADDITIONAL_CORS_ORIGINS", "")
    if additional_origins:
        # Validate and sanitize additional origins
        origins = [
            origin.strip() for origin in additional_origins.split(",") if origin.strip()
        ]
        for origin in origins:
            if _is_valid_origin(origin):
                allowed_origins.append(origin)
            else:
                logger.warning(f"Invalid CORS origin ignored: {origin}")

    # Remove duplicates while preserving order
    allowed_origins = list(dict.fromkeys(allowed_origins))

    # Secure methods - restrict to only what we need
    allowed_methods = [
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "OPTIONS",  # Required for CORS preflight
    ]

    # Secure headers - be specific about what we allow
    allowed_headers = [
        "Accept",
        "Accept-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Cache-Control",
    ]

    # Expose only necessary headers
    expose_headers = [
        "X-Total-Count",
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-Process-Time",
    ]

    logger.info(f"CORS configured for environment: {environment}")
    logger.info(f"Allowed origins: {allowed_origins}")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,  # Required for auth cookies/headers
        allow_methods=allowed_methods,
        allow_headers=allowed_headers,
        expose_headers=expose_headers,
        max_age=600,  # Cache preflight responses for 10 minutes
    )


def _is_valid_origin(origin: str) -> bool:
    """Validate that an origin is properly formatted and secure"""
    import re

    # Basic URL pattern validation
    url_pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # IP
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    if not url_pattern.match(origin):
        return False

    # Prevent potentially dangerous origins
    dangerous_patterns = [
        r"javascript:",
        r"data:",
        r"file:",
        r"ftp:",
        r"about:",
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, origin, re.IGNORECASE):
            return False

    return True
