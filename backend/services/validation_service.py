"""
Input Validation Service - Task B28
Comprehensive input validation and sanitization for SmartQuery API
"""

import logging
import re
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union

from fastapi import HTTPException
from pydantic import BaseModel, ValidationError, validator
from pydantic.networks import EmailStr

logger = logging.getLogger(__name__)


class ValidationConfig:
    """Validation configuration constants"""

    # String length limits
    MAX_PROJECT_NAME_LENGTH = 100
    MAX_PROJECT_DESCRIPTION_LENGTH = 500
    MAX_QUERY_LENGTH = 2000
    MAX_MESSAGE_LENGTH = 1000
    MAX_EMAIL_LENGTH = 254
    MAX_NAME_LENGTH = 100

    # File limits
    MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100MB
    ALLOWED_FILE_EXTENSIONS = [".csv"]
    ALLOWED_MIME_TYPES = ["text/csv", "application/csv"]

    # SQL keywords that should be filtered in user input
    DANGEROUS_SQL_KEYWORDS = [
        "DROP",
        "DELETE",
        "INSERT",
        "UPDATE",
        "ALTER",
        "CREATE",
        "TRUNCATE",
        "EXEC",
        "EXECUTE",
        "UNION",
        "SCRIPT",
        "DECLARE",
        "SHUTDOWN",
    ]

    # Patterns for malicious input detection
    MALICIOUS_PATTERNS = [
        r"<script[^>]*>.*?</script>",  # Script tags
        r"javascript:",  # JavaScript protocol
        r"vbscript:",  # VBScript protocol
        r"data:text/html",  # Data URLs with HTML
        r"on\w+\s*=",  # Event handlers
        r"\.\./|\.\.\\",  # Path traversal
        r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]",  # Control characters
    ]


class ValidationResult:
    """Result of validation operation"""

    def __init__(
        self,
        is_valid: bool,
        error_message: Optional[str] = None,
        sanitized_value: Optional[Any] = None,
    ):
        self.is_valid = is_valid
        self.error_message = error_message
        self.sanitized_value = sanitized_value


class InputSanitizer:
    """Input sanitization utilities"""

    @staticmethod
    def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
        """Sanitize string input to prevent XSS and injection attacks"""
        if not value:
            return value

        # Remove null bytes and control characters
        value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", value)

        # Strip leading/trailing whitespace
        value = value.strip()

        # Limit length if specified
        if max_length and len(value) > max_length:
            value = value[:max_length]

        # HTML encode dangerous characters
        value = value.replace("&", "&amp;")
        value = value.replace("<", "&lt;")
        value = value.replace(">", "&gt;")
        value = value.replace('"', "&quot;")
        value = value.replace("'", "&#x27;")

        return value

    @staticmethod
    def sanitize_sql_input(value: str) -> str:
        """Sanitize input that might be used in SQL contexts"""
        if not value:
            return value

        # Remove dangerous SQL keywords (case insensitive)
        for keyword in ValidationConfig.DANGEROUS_SQL_KEYWORDS:
            pattern = rf"\b{re.escape(keyword)}\b"
            value = re.sub(pattern, "", value, flags=re.IGNORECASE)

        # Remove SQL comment markers
        value = re.sub(r"--.*$", "", value, flags=re.MULTILINE)
        value = re.sub(r"/\*.*?\*/", "", value, flags=re.DOTALL)

        # Remove multiple consecutive spaces
        value = re.sub(r"\s+", " ", value)

        return InputSanitizer.sanitize_string(value)

    @staticmethod
    def detect_malicious_patterns(value: str) -> List[str]:
        """Detect potentially malicious patterns in input"""
        detected = []
        for pattern in ValidationConfig.MALICIOUS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE | re.DOTALL):
                detected.append(pattern)
        return detected


class InputValidator:
    """Main input validation service"""

    def __init__(self):
        self.sanitizer = InputSanitizer()

    def validate_uuid(self, value: str, field_name: str = "UUID") -> ValidationResult:
        """Validate UUID format"""
        if not value:
            return ValidationResult(False, f"{field_name} is required")

        try:
            uuid.UUID(str(value))
            return ValidationResult(True, sanitized_value=str(value))
        except (ValueError, AttributeError):
            return ValidationResult(False, f"Invalid {field_name} format")

    def validate_email(self, value: str) -> ValidationResult:
        """Validate email format and sanitize"""
        if not value:
            return ValidationResult(False, "Email is required")

        # Check length
        if len(value) > ValidationConfig.MAX_EMAIL_LENGTH:
            return ValidationResult(
                False,
                f"Email too long (max {ValidationConfig.MAX_EMAIL_LENGTH} characters)",
            )

        # Sanitize
        sanitized = self.sanitizer.sanitize_string(value)

        # Validate format using pydantic EmailStr
        try:
            EmailStr.validate(sanitized)
            return ValidationResult(True, sanitized_value=sanitized)
        except ValidationError:
            return ValidationResult(False, "Invalid email format")

    def validate_project_name(self, value: str) -> ValidationResult:
        """Validate project name"""
        if not value:
            return ValidationResult(False, "Project name is required")

        # Check length
        if len(value) > ValidationConfig.MAX_PROJECT_NAME_LENGTH:
            return ValidationResult(
                False,
                f"Project name too long (max {ValidationConfig.MAX_PROJECT_NAME_LENGTH} characters)",
            )

        # Check for malicious patterns
        malicious = self.sanitizer.detect_malicious_patterns(value)
        if malicious:
            return ValidationResult(False, "Project name contains invalid characters")

        # Sanitize
        sanitized = self.sanitizer.sanitize_string(
            value, ValidationConfig.MAX_PROJECT_NAME_LENGTH
        )

        if not sanitized.strip():
            return ValidationResult(False, "Project name cannot be empty")

        return ValidationResult(True, sanitized_value=sanitized)

    def validate_project_description(self, value: Optional[str]) -> ValidationResult:
        """Validate project description"""
        if not value:
            return ValidationResult(True, sanitized_value="")

        # Check length
        if len(value) > ValidationConfig.MAX_PROJECT_DESCRIPTION_LENGTH:
            return ValidationResult(
                False,
                f"Description too long (max {ValidationConfig.MAX_PROJECT_DESCRIPTION_LENGTH} characters)",
            )

        # Check for malicious patterns
        malicious = self.sanitizer.detect_malicious_patterns(value)
        if malicious:
            return ValidationResult(False, "Description contains invalid characters")

        # Sanitize
        sanitized = self.sanitizer.sanitize_string(
            value, ValidationConfig.MAX_PROJECT_DESCRIPTION_LENGTH
        )

        return ValidationResult(True, sanitized_value=sanitized)

    def validate_query_text(self, value: str) -> ValidationResult:
        """Validate natural language query text"""
        if not value:
            return ValidationResult(False, "Query text is required")

        # Check length
        if len(value) > ValidationConfig.MAX_QUERY_LENGTH:
            return ValidationResult(
                False,
                f"Query too long (max {ValidationConfig.MAX_QUERY_LENGTH} characters)",
            )

        # Check for malicious patterns
        malicious = self.sanitizer.detect_malicious_patterns(value)
        if malicious:
            return ValidationResult(
                False, "Query contains potentially malicious content"
            )

        # Sanitize for SQL context since this might be processed by LLM
        sanitized = self.sanitizer.sanitize_sql_input(value)

        if not sanitized.strip():
            return ValidationResult(False, "Query cannot be empty")

        return ValidationResult(True, sanitized_value=sanitized)

    def validate_user_name(self, value: str) -> ValidationResult:
        """Validate user display name"""
        if not value:
            return ValidationResult(False, "Name is required")

        # Check length
        if len(value) > ValidationConfig.MAX_NAME_LENGTH:
            return ValidationResult(
                False,
                f"Name too long (max {ValidationConfig.MAX_NAME_LENGTH} characters)",
            )

        # Check for malicious patterns
        malicious = self.sanitizer.detect_malicious_patterns(value)
        if malicious:
            return ValidationResult(False, "Name contains invalid characters")

        # Sanitize
        sanitized = self.sanitizer.sanitize_string(
            value, ValidationConfig.MAX_NAME_LENGTH
        )

        if not sanitized.strip():
            return ValidationResult(False, "Name cannot be empty")

        return ValidationResult(True, sanitized_value=sanitized)

    def validate_file_upload(
        self,
        filename: str,
        content_type: Optional[str] = None,
        file_size: Optional[int] = None,
    ) -> ValidationResult:
        """Validate file upload parameters"""
        if not filename:
            return ValidationResult(False, "Filename is required")

        # Sanitize filename
        sanitized_filename = self.sanitizer.sanitize_string(filename)

        # Check file extension
        file_ext = None
        if "." in sanitized_filename:
            file_ext = "." + sanitized_filename.rsplit(".", 1)[1].lower()

        if file_ext not in ValidationConfig.ALLOWED_FILE_EXTENSIONS:
            return ValidationResult(
                False,
                f"File type not allowed. Allowed: {', '.join(ValidationConfig.ALLOWED_FILE_EXTENSIONS)}",
            )

        # Check content type if provided
        if content_type and content_type not in ValidationConfig.ALLOWED_MIME_TYPES:
            return ValidationResult(
                False,
                f"Content type not allowed. Allowed: {', '.join(ValidationConfig.ALLOWED_MIME_TYPES)}",
            )

        # Check file size if provided
        if file_size and file_size > ValidationConfig.MAX_FILE_SIZE_BYTES:
            max_mb = ValidationConfig.MAX_FILE_SIZE_BYTES // (1024 * 1024)
            return ValidationResult(False, f"File too large (max {max_mb}MB)")

        return ValidationResult(True, sanitized_value=sanitized_filename)

    def validate_pagination_params(
        self, page: Optional[int] = None, page_size: Optional[int] = None
    ) -> Tuple[int, int]:
        """Validate and sanitize pagination parameters"""
        # Default values
        validated_page = 1
        validated_page_size = 20

        # Validate page
        if page is not None:
            if not isinstance(page, int) or page < 1:
                raise HTTPException(
                    status_code=400, detail="Page must be a positive integer"
                )
            if page > 1000:  # Prevent excessive pagination
                raise HTTPException(
                    status_code=400, detail="Page number too large (max 1000)"
                )
            validated_page = page

        # Validate page_size
        if page_size is not None:
            if not isinstance(page_size, int) or page_size < 1:
                raise HTTPException(
                    status_code=400, detail="Page size must be a positive integer"
                )
            if page_size > 100:  # Prevent excessive page sizes
                raise HTTPException(
                    status_code=400, detail="Page size too large (max 100)"
                )
            validated_page_size = page_size

        return validated_page, validated_page_size

    def validate_request_data(
        self,
        data: Dict[str, Any],
        required_fields: List[str] = None,
        field_validators: Dict[str, callable] = None,
    ) -> Dict[str, Any]:
        """Validate entire request data dictionary"""
        if required_fields is None:
            required_fields = []
        if field_validators is None:
            field_validators = {}

        validated_data = {}

        # Check required fields
        for field in required_fields:
            if field not in data or data[field] is None:
                raise HTTPException(
                    status_code=400, detail=f"Required field missing: {field}"
                )

        # Validate each field
        for field, value in data.items():
            if field in field_validators:
                validator_func = field_validators[field]
                result = validator_func(value)
                if not result.is_valid:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid {field}: {result.error_message}",
                    )
                validated_data[field] = result.sanitized_value
            else:
                # Default sanitization for string values
                if isinstance(value, str):
                    validated_data[field] = self.sanitizer.sanitize_string(value)
                else:
                    validated_data[field] = value

        return validated_data


class SecurityValidator:
    """Additional security-focused validation"""

    def __init__(self):
        self.input_validator = InputValidator()

    def validate_auth_token(self, token: str) -> ValidationResult:
        """Validate authentication token format"""
        if not token:
            return ValidationResult(False, "Token is required")

        # Check token format (should be JWT-like)
        if not re.match(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$", token):
            return ValidationResult(False, "Invalid token format")

        return ValidationResult(True, sanitized_value=token)

    def validate_google_oauth_token(self, token: str) -> ValidationResult:
        """Validate Google OAuth token format"""
        if not token:
            return ValidationResult(False, "Google token is required")

        # Check for mock token in development
        if token.startswith("mock_google_token"):
            return ValidationResult(True, sanitized_value=token)

        # Basic format validation for real Google tokens
        if len(token) < 100 or len(token) > 2048:
            return ValidationResult(False, "Invalid Google token format")

        # Should not contain dangerous characters
        if re.search(r'[<>"\']', token):
            return ValidationResult(False, "Invalid Google token format")

        return ValidationResult(True, sanitized_value=token)

    def check_sql_injection_attempt(self, text: str) -> bool:
        """Check if text contains SQL injection attempts"""
        dangerous_patterns = [
            r"\bUNION\s+SELECT\b",
            r"\bDROP\s+TABLE\b",
            r"\bDELETE\s+FROM\b",
            r"\bINSERT\s+INTO\b",
            r"\bUPDATE\s+.*\bSET\b",
            r"\bALTER\s+TABLE\b",
            r"\bCREATE\s+TABLE\b",
            r";.*--",
            r"/\*.*\*/",
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Potential SQL injection detected: {pattern}")
                return True

        return False


# Global validator instances
input_validator = InputValidator()
security_validator = SecurityValidator()


def validate_and_sanitize_input(
    data: Any, validation_rules: Dict[str, Any] = None
) -> Any:
    """Main entry point for input validation and sanitization"""
    if validation_rules is None:
        validation_rules = {}

    try:
        if isinstance(data, dict):
            return input_validator.validate_request_data(data, **validation_rules)
        elif isinstance(data, str):
            return input_validator.sanitizer.sanitize_string(data)
        else:
            return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Input validation error: {str(e)}")
        raise HTTPException(status_code=400, detail="Input validation failed")


# Pydantic models for request validation
class ValidatedProjectCreate(BaseModel):
    """Validated project creation request"""

    name: str
    description: Optional[str] = None

    @validator("name")
    def validate_name(cls, v):
        result = input_validator.validate_project_name(v)
        if not result.is_valid:
            raise ValueError(result.error_message)
        return result.sanitized_value

    @validator("description")
    def validate_description(cls, v):
        if v is None:
            return None
        result = input_validator.validate_project_description(v)
        if not result.is_valid:
            raise ValueError(result.error_message)
        return result.sanitized_value


class ValidatedChatMessage(BaseModel):
    """Validated chat message request"""

    message: str

    @validator("message")
    def validate_message(cls, v):
        result = input_validator.validate_query_text(v)
        if not result.is_valid:
            raise ValueError(result.error_message)
        return result.sanitized_value


class ValidatedUserProfile(BaseModel):
    """Validated user profile data"""

    name: str
    email: str

    @validator("name")
    def validate_name(cls, v):
        result = input_validator.validate_user_name(v)
        if not result.is_valid:
            raise ValueError(result.error_message)
        return result.sanitized_value

    @validator("email")
    def validate_email(cls, v):
        result = input_validator.validate_email(v)
        if not result.is_valid:
            raise ValueError(result.error_message)
        return result.sanitized_value
