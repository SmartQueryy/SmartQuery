"""
Enhanced Error Response Middleware - Task B28

Standardizes all HTTP error responses to use the ApiResponse format,
ensuring consistent error handling across all API endpoints with
enhanced security measures and comprehensive logging.
"""

import logging
import os
import traceback
from datetime import datetime
from typing import Any, Dict, Optional

import jwt
from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from models.response_schemas import ApiResponse

# Configure logging for error handling
error_logger = logging.getLogger("error_handler")
security_logger = logging.getLogger("security_errors")


class SecurityErrorTracker:
    """Track security-related errors for monitoring"""

    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.is_production = self.environment == "production"

    def log_security_error(
        self, request: Request, error_type: str, details: Dict[str, Any]
    ) -> None:
        """Log security-related errors"""
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")

        security_event = {
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": error_type,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "path": str(request.url.path),
            "method": request.method,
            "details": details,
        }

        security_logger.warning(f"SECURITY_ERROR: {security_event}")

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        if hasattr(request, "client") and request.client:
            return request.client.host

        return "unknown"

    def sanitize_error_message(self, message: str) -> str:
        """Sanitize error messages to prevent information leakage"""
        if self.is_production:
            # In production, return generic error messages for security
            sensitive_patterns = [
                r"password",
                r"secret",
                r"key",
                r"token",
                r"credential",
                r"database",
                r"connection",
                r"sql",
                r"query",
            ]

            import re

            for pattern in sensitive_patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    return "An error occurred while processing your request"

        return message


def setup_error_handlers(app: FastAPI):
    """Setup comprehensive error handlers for the FastAPI app"""

    error_tracker = SecurityErrorTracker()

    @app.exception_handler(HTTPException)
    async def custom_http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTPException with enhanced security and logging"""

        # Log security-related errors
        if exc.status_code in [401, 403, 429]:
            error_tracker.log_security_error(
                request,
                "auth_error",
                {"status_code": exc.status_code, "detail": str(exc.detail)},
            )

        # Sanitize error message
        error_detail = error_tracker.sanitize_error_message(
            exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        )

        error_response = ApiResponse[None](
            success=False,
            error=error_detail,
            message=_get_error_message(exc.status_code),
            data=None,
        )

        # Add security headers to error responses
        response = JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump(),
            headers=getattr(exc, "headers", None),
        )

        _add_security_headers(response)
        return response

    @app.exception_handler(StarletteHTTPException)
    async def custom_starlette_exception_handler(
        request: Request, exc: StarletteHTTPException
    ):
        """Handle Starlette HTTPException with enhanced security"""

        # Sanitize error message
        error_detail = error_tracker.sanitize_error_message(
            exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        )

        error_response = ApiResponse[None](
            success=False,
            error=error_detail,
            message=_get_error_message(exc.status_code),
            data=None,
        )

        response = JSONResponse(
            status_code=exc.status_code, content=error_response.model_dump()
        )

        _add_security_headers(response)
        return response

    @app.exception_handler(RequestValidationError)
    async def custom_validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """Handle validation errors with enhanced security"""

        # Log potential injection attempts
        error_tracker.log_security_error(
            request,
            "validation_error",
            {
                "error_count": len(exc.errors()),
                "errors": [
                    {
                        "field": " -> ".join(str(x) for x in error["loc"]),
                        "type": error["type"],
                    }
                    for error in exc.errors()[:5]
                ],  # Limit logged errors
            },
        )

        # Format validation errors securely
        error_details = []
        for error in exc.errors():
            field = " -> ".join(str(x) for x in error["loc"])
            message = error["msg"]

            # Sanitize field names and messages
            field = error_tracker.sanitize_error_message(field)
            message = error_tracker.sanitize_error_message(message)

            error_details.append(f"{field}: {message}")

        error_message = "; ".join(error_details[:3])  # Limit to first 3 errors
        if len(exc.errors()) > 3:
            error_message += f" (and {len(exc.errors()) - 3} more errors)"

        error_response = ApiResponse[None](
            success=False, error=error_message, message="Validation Error", data=None
        )

        response = JSONResponse(status_code=422, content=error_response.model_dump())

        _add_security_headers(response)
        return response

    @app.exception_handler(ValidationError)
    async def custom_pydantic_validation_handler(
        request: Request, exc: ValidationError
    ):
        """Handle Pydantic validation errors"""

        error_tracker.log_security_error(
            request,
            "pydantic_validation_error",
            {
                "error_count": len(exc.errors()),
            },
        )

        error_response = ApiResponse[None](
            success=False,
            error="Invalid input data format",
            message="Validation Error",
            data=None,
        )

        response = JSONResponse(status_code=400, content=error_response.model_dump())

        _add_security_headers(response)
        return response

    @app.exception_handler(jwt.InvalidTokenError)
    async def custom_jwt_exception_handler(
        request: Request, exc: jwt.InvalidTokenError
    ):
        """Handle JWT token errors"""

        error_tracker.log_security_error(request, "jwt_error", {"error": str(exc)})

        error_response = ApiResponse[None](
            success=False,
            error="Invalid or expired authentication token",
            message="Authentication Error",
            data=None,
        )

        response = JSONResponse(
            status_code=401,
            content=error_response.model_dump(),
            headers={"WWW-Authenticate": "Bearer"},
        )

        _add_security_headers(response)
        return response

    @app.exception_handler(Exception)
    async def custom_general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions with comprehensive logging and security"""

        # Generate error ID for tracking
        import uuid

        error_id = str(uuid.uuid4())[:8]

        # Log full error details for debugging
        error_details = {
            "error_id": error_id,
            "exception_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": (
                traceback.format_exc() if not error_tracker.is_production else "Hidden"
            ),
        }

        error_logger.error(f"UNHANDLED_EXCEPTION: {error_details}")

        # Log as security event if it might be an attack
        if any(
            keyword in str(exc).lower()
            for keyword in [
                "injection",
                "script",
                "eval",
                "exec",
                "import",
                "open",
                "file",
            ]
        ):
            error_tracker.log_security_error(
                request,
                "potential_attack",
                {"error_id": error_id, "exception_type": type(exc).__name__},
            )

        # Return sanitized error response
        if error_tracker.is_production:
            error_message = f"An internal error occurred. Reference ID: {error_id}"
        else:
            error_message = f"Internal server error: {str(exc)}"

        error_response = ApiResponse[None](
            success=False,
            error=error_message,
            message="Internal Server Error",
            data=None,
        )

        response = JSONResponse(status_code=500, content=error_response.model_dump())

        _add_security_headers(response)
        return response


def _add_security_headers(response: JSONResponse) -> None:
    """Add security headers to error responses"""
    security_headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }

    for header, value in security_headers.items():
        response.headers[header] = value


def _get_error_message(status_code: int) -> str:
    """Get appropriate error message based on status code"""

    error_messages = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        408: "Request Timeout",
        409: "Conflict",
        413: "Payload Too Large",
        415: "Unsupported Media Type",
        422: "Validation Error",
        429: "Too Many Requests",
        500: "Internal Server Error",
        502: "Bad Gateway",
        503: "Service Unavailable",
        504: "Gateway Timeout",
    }

    return error_messages.get(status_code, f"HTTP {status_code} Error")
