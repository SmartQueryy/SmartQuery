"""
Error Response Middleware

Standardizes all HTTP error responses to use the ApiResponse format,
ensuring consistent error handling across all API endpoints.

Note: This needs to be implemented using FastAPI exception handlers
instead of middleware, as middleware cannot catch HTTPExceptions
raised by FastAPI's validation and routing.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from models.response_schemas import ApiResponse


def setup_error_handlers(app: FastAPI):
    """Setup standardized error handlers for the FastAPI app"""

    @app.exception_handler(HTTPException)
    async def custom_http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTPException with standardized ApiResponse format"""

        error_response = ApiResponse[None](
            success=False,
            error=exc.detail if isinstance(exc.detail, str) else str(exc.detail),
            message=_get_error_message(exc.status_code),
            data=None,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump(),
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(StarletteHTTPException)
    async def custom_starlette_exception_handler(
        request: Request, exc: StarletteHTTPException
    ):
        """Handle Starlette HTTPException with standardized ApiResponse format"""

        error_response = ApiResponse[None](
            success=False,
            error=exc.detail if isinstance(exc.detail, str) else str(exc.detail),
            message=_get_error_message(exc.status_code),
            data=None,
        )

        return JSONResponse(
            status_code=exc.status_code, content=error_response.model_dump()
        )

    @app.exception_handler(RequestValidationError)
    async def custom_validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """Handle validation errors with standardized ApiResponse format"""

        # Format validation errors into a readable message
        error_details = []
        for error in exc.errors():
            field = " -> ".join(str(x) for x in error["loc"])
            message = error["msg"]
            error_details.append(f"{field}: {message}")

        error_message = "; ".join(error_details)

        error_response = ApiResponse[None](
            success=False, error=error_message, message="Validation Error", data=None
        )

        return JSONResponse(status_code=422, content=error_response.model_dump())

    @app.exception_handler(Exception)
    async def custom_general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions with standardized ApiResponse format"""

        # Log the actual error for debugging (in production, use proper logging)
        print(f"Unexpected error: {str(exc)}")

        error_response = ApiResponse[None](
            success=False,
            error="Internal server error",
            message="An unexpected error occurred",
            data=None,
        )

        return JSONResponse(status_code=500, content=error_response.model_dump())


def _get_error_message(status_code: int) -> str:
    """Get appropriate error message based on status code"""

    error_messages = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        422: "Validation Error",
        500: "Internal Server Error",
    }

    return error_messages.get(status_code, f"HTTP {status_code} Error")
