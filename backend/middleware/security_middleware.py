"""
Security Middleware for SmartQuery API - Task B28
Implements comprehensive security measures including headers, rate limiting,
input validation, and request sanitization.
"""

import hashlib
import json
import logging
import os
import re
import time
import uuid
from collections import defaultdict, deque
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, List, Optional, Set, Tuple

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logging
logger = logging.getLogger(__name__)


class SecurityConfig:
    """Security configuration settings"""

    def __init__(self):
        self.security_headers_enabled = (
            os.getenv("SECURITY_HEADERS_ENABLED", "true").lower() == "true"
        )
        self.rate_limit_enabled = (
            os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
        )
        self.rate_limit_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
        self.max_request_size = int(
            os.getenv("MAX_REQUEST_SIZE_BYTES", "10485760")
        )  # 10MB
        self.max_query_length = int(os.getenv("MAX_QUERY_LENGTH", "2000"))
        self.blocked_patterns = self._load_blocked_patterns()
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.strict_mode = self.environment == "production"

    def _load_blocked_patterns(self) -> List[str]:
        """Load patterns that should be blocked in requests"""
        return [
            # SQL Injection patterns
            r"(\bUNION\b.*\bSELECT\b)",
            r"(\bDROP\b.*\bTABLE\b)",
            r"(\bDELETE\b.*\bFROM\b)",
            r"(\bINSERT\b.*\bINTO\b)",
            r"(\bUPDATE\b.*\bSET\b)",
            r"(\bALTER\b.*\bTABLE\b)",
            r"(\bCREATE\b.*\bTABLE\b)",
            r"(\bTRUNCATE\b.*\bTABLE\b)",
            # Script injection patterns
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"vbscript:",
            r"onload=",
            r"onerror=",
            r"onclick=",
            # Path traversal patterns
            r"\.\./",
            r"\.\.\\",
            # Command injection patterns
            r"[;&|`$]",
            r"\|\|",
            r"&&",
        ]


class RateLimiter:
    """Enhanced rate limiting with different limits for different endpoints"""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.blocked_ips: Set[str] = set()
        self.endpoint_limits = {
            "/chat/": 20,  # Slower limit for AI processing
            "/projects": 50,  # Medium limit for project operations
            "/auth/": 30,  # Medium limit for auth operations
            "default": config.rate_limit_per_minute,
        }

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address with proxy support"""
        # Check for forwarded headers (common in production)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct connection IP
        if hasattr(request, "client") and request.client:
            return request.client.host

        return "unknown"

    def _get_rate_limit_for_path(self, path: str) -> int:
        """Get rate limit for specific endpoint path"""
        for endpoint_pattern, limit in self.endpoint_limits.items():
            if endpoint_pattern != "default" and endpoint_pattern in path:
                return limit
        return self.endpoint_limits["default"]

    def _clean_old_requests(self, ip: str, now: float) -> None:
        """Remove requests older than 1 minute"""
        cutoff = now - 60
        while self.requests[ip] and self.requests[ip][0] < cutoff:
            self.requests[ip].popleft()

    def is_rate_limited(self, request: Request) -> Tuple[bool, Dict[str, Any]]:
        """Check if request should be rate limited"""
        if not self.config.rate_limit_enabled:
            return False, {}

        ip = self._get_client_ip(request)
        now = time.time()
        path = str(request.url.path)

        # Check if IP is blocked
        if ip in self.blocked_ips:
            return True, {
                "reason": "IP temporarily blocked",
                "retry_after": 300,  # 5 minutes
            }

        # Clean old requests
        self._clean_old_requests(ip, now)

        # Get rate limit for this endpoint
        rate_limit = self._get_rate_limit_for_path(path)

        # Count recent requests
        current_requests = len(self.requests[ip])

        if current_requests >= rate_limit:
            # Block IP if they're consistently hitting limits
            if current_requests >= rate_limit * 2:
                self.blocked_ips.add(ip)
                logger.warning(f"IP {ip} blocked for excessive requests")

            return True, {
                "reason": "Rate limit exceeded",
                "limit": rate_limit,
                "current": current_requests,
                "retry_after": 60,
            }

        # Add current request
        self.requests[ip].append(now)

        return False, {
            "limit": rate_limit,
            "current": current_requests + 1,
            "remaining": rate_limit - current_requests - 1,
        }


class InputValidator:
    """Input validation and sanitization"""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.blocked_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in config.blocked_patterns
        ]

    def validate_request_size(self, content_length: Optional[int]) -> bool:
        """Validate request size doesn't exceed limits"""
        if content_length is None:
            return True
        return content_length <= self.config.max_request_size

    def sanitize_input(self, data: Any) -> Any:
        """Recursively sanitize input data"""
        if isinstance(data, dict):
            return {key: self.sanitize_input(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_input(item) for item in data]
        elif isinstance(data, str):
            return self._sanitize_string(data)
        else:
            return data

    def _sanitize_string(self, text: str) -> str:
        """Sanitize string input"""
        if not text:
            return text

        # Limit length
        if len(text) > self.config.max_query_length:
            raise HTTPException(
                status_code=400,
                detail=f"Input too long. Maximum length: {self.config.max_query_length}",
            )

        # Check for blocked patterns
        for pattern in self.blocked_patterns:
            if pattern.search(text):
                logger.warning(f"Blocked malicious pattern in input: {pattern.pattern}")
                raise HTTPException(
                    status_code=400,
                    detail="Input contains potentially malicious content",
                )

        # Basic HTML entity encoding for XSS prevention
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        text = text.replace("&", "&amp;")
        text = text.replace('"', "&quot;")
        text = text.replace("'", "&#x27;")

        return text

    def validate_json_structure(
        self, data: Dict[str, Any], max_depth: int = 10
    ) -> bool:
        """Validate JSON structure to prevent deeply nested attacks"""

        def check_depth(obj, current_depth):
            if current_depth > max_depth:
                return False
            if isinstance(obj, dict):
                return all(
                    check_depth(value, current_depth + 1) for value in obj.values()
                )
            elif isinstance(obj, list):
                return all(check_depth(item, current_depth + 1) for item in obj)
            return True

        return check_depth(data, 0)


class SecurityHeadersMiddleware:
    """Add security headers to responses"""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.csp_nonce = None

    def _generate_nonce(self) -> str:
        """Generate a random nonce for CSP"""
        return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:16]

    def add_security_headers(self, response: Response, request: Request) -> None:
        """Add comprehensive security headers"""
        if not self.config.security_headers_enabled:
            return

        # Generate nonce for this request
        self.csp_nonce = self._generate_nonce()

        # Content Security Policy
        csp_policy = (
            f"default-src 'self'; "
            f"script-src 'self' 'nonce-{self.csp_nonce}' 'unsafe-inline'; "
            f"style-src 'self' 'unsafe-inline'; "
            f"img-src 'self' data: https:; "
            f"font-src 'self' https:; "
            f"connect-src 'self' https:; "
            f"frame-ancestors 'none'; "
            f"base-uri 'self'"
        )

        security_headers = {
            # Prevent XSS attacks
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            # Content Security Policy
            "Content-Security-Policy": csp_policy,
            # HTTPS enforcement (in production)
            "Strict-Transport-Security": (
                "max-age=31536000; includeSubDomains; preload"
                if self.config.strict_mode
                else "max-age=3600"
            ),
            # Prevent MIME type confusion
            "X-Content-Type-Options": "nosniff",
            # Referrer policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            # Feature policy
            "Permissions-Policy": (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=(), "
                "magnetometer=(), "
                "gyroscope=(), "
                "speaker=()"
            ),
            # Custom security headers
            "X-SmartQuery-Version": "1.0.0",
            "X-Security-Scan": "passed",
        }

        # Add all security headers
        for header, value in security_headers.items():
            response.headers[header] = value

        # Add rate limiting headers if available
        if hasattr(request.state, "rate_limit_info"):
            rate_info = request.state.rate_limit_info
            response.headers["X-RateLimit-Limit"] = str(rate_info.get("limit", ""))
            response.headers["X-RateLimit-Remaining"] = str(
                rate_info.get("remaining", "")
            )
            if "retry_after" in rate_info:
                response.headers["Retry-After"] = str(rate_info["retry_after"])


class SecurityMiddleware(BaseHTTPMiddleware):
    """Comprehensive security middleware"""

    def __init__(self, app):
        super().__init__(app)
        self.config = SecurityConfig()
        self.rate_limiter = RateLimiter(self.config)
        self.input_validator = InputValidator(self.config)
        self.headers_middleware = SecurityHeadersMiddleware(self.config)

        logger.info(
            f"SecurityMiddleware initialized - Environment: {self.config.environment}"
        )
        logger.info(f"Rate limiting: {self.config.rate_limit_enabled}")
        logger.info(f"Security headers: {self.config.security_headers_enabled}")

    async def dispatch(self, request: Request, call_next):
        """Process request through security pipeline"""
        start_time = time.time()

        try:
            # 1. Validate request size
            content_length = request.headers.get("content-length")
            if content_length and not self.input_validator.validate_request_size(
                int(content_length)
            ):
                raise HTTPException(
                    status_code=413,
                    detail=f"Request too large. Maximum size: {self.config.max_request_size} bytes",
                )

            # 2. Check rate limiting
            is_limited, rate_info = self.rate_limiter.is_rate_limited(request)
            if is_limited:
                response = Response(
                    content=json.dumps(
                        {
                            "success": False,
                            "error": rate_info.get("reason", "Rate limit exceeded"),
                            "data": None,
                        }
                    ),
                    status_code=429,
                    media_type="application/json",
                )

                if "retry_after" in rate_info:
                    response.headers["Retry-After"] = str(rate_info["retry_after"])

                return response

            # Store rate limit info for headers
            request.state.rate_limit_info = rate_info

            # 3. Validate and sanitize request body (for POST/PUT requests)
            if request.method in ["POST", "PUT", "PATCH"]:
                await self._validate_request_body(request)

            # 4. Process request
            response = await call_next(request)

            # 5. Add security headers
            self.headers_middleware.add_security_headers(response, request)

            # 6. Log security events
            processing_time = time.time() - start_time
            if processing_time > 5.0:  # Log slow requests
                logger.warning(
                    f"Slow request: {request.method} {request.url.path} "
                    f"took {processing_time:.2f}s"
                )

            return response

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Security middleware error: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal security error")

    async def _validate_request_body(self, request: Request) -> None:
        """Validate request body for security threats"""
        try:
            if request.headers.get("content-type", "").startswith("application/json"):
                # Read and validate JSON body
                body = await request.body()
                if body:
                    try:
                        data = json.loads(body)

                        # Check JSON structure depth
                        if not self.input_validator.validate_json_structure(data):
                            raise HTTPException(
                                status_code=400, detail="Request structure too complex"
                            )

                        # Sanitize input data
                        sanitized_data = self.input_validator.sanitize_input(data)

                        # Replace request body with sanitized version
                        request._body = json.dumps(sanitized_data).encode()

                    except json.JSONDecodeError:
                        raise HTTPException(
                            status_code=400, detail="Invalid JSON format"
                        )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Request body validation error: {str(e)}")
            raise HTTPException(status_code=400, detail="Request validation failed")


# Security decorator for additional endpoint protection
def require_security_check(strict: bool = False):
    """Decorator for additional security checks on sensitive endpoints"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Additional security logic can be added here
            # For example: CAPTCHA verification, additional rate limiting, etc.
            return await func(*args, **kwargs)

        return wrapper

    return decorator


# Utility functions for security
def hash_sensitive_data(data: str) -> str:
    """Hash sensitive data for logging/storage"""
    return hashlib.sha256(data.encode()).hexdigest()


def validate_uuid(uuid_string: str) -> bool:
    """Validate UUID format"""
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False


def sanitize_log_data(data: Any) -> Any:
    """Sanitize data before logging to prevent log injection"""
    if isinstance(data, str):
        # Remove newlines and control characters
        return re.sub(r"[\r\n\t\x00-\x1f\x7f-\x9f]", "", str(data))
    return data


class SecurityAuditLogger:
    """Audit logger for security events"""

    def __init__(self):
        self.audit_logger = logging.getLogger("security_audit")

    def log_security_event(
        self,
        event_type: str,
        details: Dict[str, Any],
        request: Optional[Request] = None,
    ) -> None:
        """Log security-related events"""
        event_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "details": sanitize_log_data(details),
        }

        if request:
            event_data.update(
                {
                    "ip_address": (
                        self.rate_limiter._get_client_ip(request)
                        if hasattr(self, "rate_limiter")
                        else "unknown"
                    ),
                    "user_agent": request.headers.get("user-agent", "unknown"),
                    "path": str(request.url.path),
                    "method": request.method,
                }
            )

        self.audit_logger.info(f"SECURITY_EVENT: {json.dumps(event_data)}")


# Global instances
security_audit = SecurityAuditLogger()


def setup_security_middleware(app):
    """Setup security middleware on FastAPI app"""
    app.add_middleware(SecurityMiddleware)
    logger.info("Security middleware configured successfully")
