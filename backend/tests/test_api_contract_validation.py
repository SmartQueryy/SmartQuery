"""
API Contract Validation Tests - Task B25

This comprehensive test suite validates that all backend endpoints conform
to the API contract defined in shared/api-contract.ts, ensuring complete
frontend-backend compatibility.
"""

import uuid
from datetime import datetime
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from main import app
from middleware.auth_middleware import verify_token
from models.project import ProjectCreate
from models.user import GoogleOAuthData, UserInDB
from services.auth_service import AuthService
from services.project_service import get_project_service
from services.user_service import get_user_service

client = TestClient(app)

# Initialize services for testing
auth_service = AuthService()
project_service = get_project_service()
user_service = get_user_service()


def mock_verify_token():
    """Mock verify_token that returns test user UUID as string"""
    return "00000000-0000-0000-0000-000000000001"


@pytest.fixture
def sample_user():
    """Sample user for testing"""
    test_user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    return UserInDB(
        id=test_user_id,
        email="test@example.com",
        name="Test User",
        avatar_url="https://example.com/avatar.jpg",
        google_id="google_123",
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def test_access_token():
    """Create a valid access token for testing"""
    test_user_id = "00000000-0000-0000-0000-000000000001"
    return auth_service.create_access_token(test_user_id, "test@example.com")


@pytest.fixture
def test_user_in_db():
    """Create a test user for validation"""
    test_user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    return UserInDB(
        id=test_user_id,
        email="test@example.com",
        name="Test User",
        avatar_url="https://example.com/avatar.jpg",
        google_id="google_123",
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def test_project():
    """Create a test project mock"""
    project_id = uuid.uuid4()
    user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

    return Mock(
        id=project_id,
        user_id=user_id,
        name="Test Project",
        description="Test project for validation",
        csv_filename="test.csv",
        csv_path="test/path/test.csv",
        row_count=100,
        column_count=5,
        columns_metadata=[
            {
                "name": "test_column",
                "type": "string",
                "nullable": False,
                "sample_values": ["value1", "value2", "value3"],
            }
        ],
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
        status="ready",
    )


def validate_api_response_structure(response_data: Dict[str, Any]) -> None:
    """Validate that response follows ApiResponse<T> contract structure"""
    assert "success" in response_data, "Response must have 'success' field"
    assert isinstance(response_data["success"], bool), "success must be boolean"

    # At least one of data, error, or message should be present
    has_content = any(
        field in response_data and response_data[field] is not None
        for field in ["data", "error", "message"]
    )
    assert has_content, "Response must have at least one of: data, error, message"

    # If success is True, should have data
    if response_data["success"]:
        assert "data" in response_data, "Successful response should have 'data' field"

    # If success is False, should have error
    if not response_data["success"]:
        assert "error" in response_data, "Failed response should have 'error' field"


def validate_user_structure(user_data: Dict[str, Any]) -> None:
    """Validate User object structure against API contract"""
    required_fields = ["id", "email", "name", "created_at"]
    optional_fields = ["avatar_url", "last_sign_in_at"]

    for field in required_fields:
        assert field in user_data, f"User must have required field: {field}"
        assert user_data[field] is not None, f"User.{field} cannot be null"

    for field in optional_fields:
        if field in user_data and user_data[field] is not None:
            assert isinstance(
                user_data[field], str
            ), f"User.{field} must be string when present"


def validate_project_structure(project_data: Dict[str, Any]) -> None:
    """Validate Project object structure against API contract"""
    required_fields = [
        "id",
        "user_id",
        "name",
        "csv_filename",
        "csv_path",
        "row_count",
        "column_count",
        "columns_metadata",
        "created_at",
        "updated_at",
        "status",
    ]
    optional_fields = ["description"]

    for field in required_fields:
        assert field in project_data, f"Project must have required field: {field}"

    # Validate status enum
    valid_statuses = ["uploading", "processing", "ready", "error"]
    assert (
        project_data["status"] in valid_statuses
    ), f"Invalid project status: {project_data['status']}"

    # Validate columns_metadata structure
    if project_data["columns_metadata"]:
        for column in project_data["columns_metadata"]:
            validate_column_metadata_structure(column)


def validate_column_metadata_structure(column_data: Dict[str, Any]) -> None:
    """Validate ColumnMetadata structure against API contract"""
    required_fields = ["name", "type", "nullable", "sample_values"]
    optional_fields = ["unique_count", "min_value", "max_value"]

    for field in required_fields:
        assert field in column_data, f"ColumnMetadata must have required field: {field}"

    # Validate type enum
    valid_types = ["string", "number", "boolean", "date", "datetime"]
    assert (
        column_data["type"] in valid_types
    ), f"Invalid column type: {column_data['type']}"


def validate_pagination_response(response_data: Dict[str, Any]) -> None:
    """Validate PaginatedResponse structure against API contract"""
    required_fields = ["items", "total", "page", "limit", "hasMore"]

    for field in required_fields:
        assert field in response_data, f"PaginatedResponse must have field: {field}"

    assert isinstance(response_data["items"], list), "items must be a list"
    assert isinstance(response_data["total"], int), "total must be an integer"
    assert isinstance(response_data["page"], int), "page must be an integer"
    assert isinstance(response_data["limit"], int), "limit must be an integer"
    assert isinstance(response_data["hasMore"], bool), "hasMore must be boolean"


class TestAuthenticationEndpointsContract:
    """Test authentication endpoints against API contract"""

    def test_get_me_endpoint_contract(self, test_user_in_db, test_access_token):
        """Test GET /auth/me endpoint contract compliance"""
        app.dependency_overrides[verify_token] = mock_verify_token

        # Mock the auth service get_current_user method
        with patch("api.auth.auth_service.get_current_user") as mock_get_user:
            mock_get_user.return_value = test_user_in_db

            try:
                response = client.get(
                    "/auth/me",
                    headers={"Authorization": f"Bearer {test_access_token}"},
                )

                assert response.status_code == 200
                data = response.json()

                # Validate ApiResponse structure
                validate_api_response_structure(data)

                # Validate User structure
                validate_user_structure(data["data"])

                # Validate required User fields match expected types
                user_data = data["data"]
                assert isinstance(user_data["id"], str)
                assert isinstance(user_data["email"], str)
                assert isinstance(user_data["name"], str)
                assert isinstance(user_data["created_at"], str)

            finally:
                app.dependency_overrides.clear()

    @patch("services.auth_service.AuthService.login_with_google")
    def test_google_login_endpoint_contract(self, mock_login):
        """Test POST /auth/google endpoint contract compliance"""
        # Mock successful Google login
        mock_user = UserInDB(
            id=uuid.uuid4(),
            email="test@example.com",
            name="Test User",
            avatar_url="https://example.com/avatar.jpg",
            google_id="google_123",
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        mock_login.return_value = (
            mock_user,
            "mock_access_token",
            "mock_refresh_token",
            True,
        )

        response = client.post(
            "/auth/google", json={"google_token": "mock_google_token"}
        )

        assert response.status_code == 200
        data = response.json()

        # Validate ApiResponse structure
        validate_api_response_structure(data)

        # Validate AuthResponse structure
        auth_data = data["data"]
        required_fields = ["user", "access_token", "refresh_token", "expires_in"]

        for field in required_fields:
            assert field in auth_data, f"AuthResponse must have field: {field}"

        # Validate User structure within AuthResponse
        validate_user_structure(auth_data["user"])

        # Validate token fields
        assert isinstance(auth_data["access_token"], str)
        assert isinstance(auth_data["refresh_token"], str)
        assert isinstance(auth_data["expires_in"], int)

    def test_logout_endpoint_contract(self, test_user_in_db, test_access_token):
        """Test POST /auth/logout endpoint contract compliance"""
        app.dependency_overrides[verify_token] = mock_verify_token

        # Mock the auth service methods
        with (
            patch("api.auth.auth_service.get_current_user") as mock_get_user,
            patch("api.auth.auth_service.revoke_user_tokens") as mock_revoke,
        ):
            mock_get_user.return_value = test_user_in_db
            mock_revoke.return_value = True

            try:
                response = client.post(
                    "/auth/logout",
                    headers={"Authorization": f"Bearer {test_access_token}"},
                )

                assert response.status_code == 200
                data = response.json()

                # Validate ApiResponse structure
                validate_api_response_structure(data)

                # Validate logout response structure
                assert "message" in data["data"]
                assert isinstance(data["data"]["message"], str)

            finally:
                app.dependency_overrides.clear()


class TestProjectEndpointsContract:
    """Test project endpoints against API contract"""

    def test_get_projects_endpoint_contract(self, test_user_in_db, test_access_token):
        """Test GET /projects endpoint contract compliance"""
        app.dependency_overrides[verify_token] = mock_verify_token

        try:
            response = client.get(
                "/projects?page=1&limit=20",
                headers={"Authorization": f"Bearer {test_access_token}"},
            )

            assert response.status_code == 200
            data = response.json()

            # Validate ApiResponse structure
            validate_api_response_structure(data)

            # Validate PaginatedResponse structure
            validate_pagination_response(data["data"])

            # Validate Project structures in items
            for project in data["data"]["items"]:
                validate_project_structure(project)

        finally:
            app.dependency_overrides.clear()

    def test_create_project_endpoint_contract(self, test_user_in_db, test_access_token):
        """Test POST /projects endpoint contract compliance"""
        app.dependency_overrides[verify_token] = mock_verify_token

        try:
            response = client.post(
                "/projects",
                json={
                    "name": "Test Contract Project",
                    "description": "Testing API contract compliance",
                },
                headers={"Authorization": f"Bearer {test_access_token}"},
            )

            assert response.status_code == 200
            data = response.json()

            # Validate ApiResponse structure
            validate_api_response_structure(data)

            # Validate CreateProjectResponse structure
            create_response = data["data"]
            required_fields = ["project", "upload_url", "upload_fields"]

            for field in required_fields:
                assert (
                    field in create_response
                ), f"CreateProjectResponse must have field: {field}"

            # Validate Project structure
            validate_project_structure(create_response["project"])

            # Validate upload fields
            assert isinstance(create_response["upload_url"], str)
            assert isinstance(create_response["upload_fields"], dict)

        finally:
            app.dependency_overrides.clear()

    def test_get_project_endpoint_contract(
        self, test_user_in_db, test_access_token, test_project
    ):
        """Test GET /projects/{id} endpoint contract compliance"""
        app.dependency_overrides[verify_token] = mock_verify_token

        # Mock project service and ProjectPublic
        with (
            patch("api.projects.project_service") as mock_service,
            patch("api.projects.ProjectPublic") as mock_project_public,
        ):

            # Mock database project
            mock_db_project = Mock()
            mock_db_project.user_id = test_user_in_db.id
            mock_service.get_project_by_id.return_value = mock_db_project

            # Mock ProjectPublic conversion with actual values not Mock objects
            mock_project_api = Mock()
            mock_project_api.id = str(test_project.id)
            mock_project_api.user_id = str(test_user_in_db.id)
            mock_project_api.name = "Test Project"  # Real string
            mock_project_api.description = "Test project for validation"  # Real string
            mock_project_api.csv_filename = "test.csv"  # Real string
            mock_project_api.csv_path = "test/path/test.csv"  # Real string
            mock_project_api.row_count = 100  # Real int
            mock_project_api.column_count = 5  # Real int
            mock_project_api.columns_metadata = [
                {
                    "name": "test_column",
                    "type": "string",
                    "nullable": False,
                    "sample_values": ["value1", "value2", "value3"],
                }
            ]  # Real list
            mock_project_api.created_at = datetime.utcnow().isoformat()  # Real string
            mock_project_api.updated_at = datetime.utcnow().isoformat()  # Real string
            mock_project_api.status = "ready"  # Real string

            mock_project_public.from_db_project.return_value = mock_project_api

            try:
                response = client.get(
                    f"/projects/{test_project.id}",
                    headers={"Authorization": f"Bearer {test_access_token}"},
                )

                assert response.status_code == 200
                data = response.json()

                # Validate ApiResponse structure
                validate_api_response_structure(data)

                # Validate Project structure
                validate_project_structure(data["data"])

            finally:
                app.dependency_overrides.clear()

    def test_project_status_endpoint_contract(
        self, test_user_in_db, test_access_token, test_project
    ):
        """Test GET /projects/{id}/status endpoint contract compliance"""
        app.dependency_overrides[verify_token] = mock_verify_token

        # Mock project service
        with patch("api.projects.project_service") as mock_service:
            mock_service.get_project_by_id.return_value = test_project

            try:
                response = client.get(
                    f"/projects/{test_project.id}/status",
                    headers={"Authorization": f"Bearer {test_access_token}"},
                )

                assert response.status_code == 200
                data = response.json()

                # Validate ApiResponse structure
                validate_api_response_structure(data)

                # Validate UploadStatusResponse structure
                status_data = data["data"]
                required_fields = ["project_id", "status", "progress"]
                optional_fields = ["message", "error"]

                for field in required_fields:
                    assert (
                        field in status_data
                    ), f"UploadStatusResponse must have field: {field}"

                # Validate field types
                assert isinstance(status_data["project_id"], str)
                assert status_data["status"] in [
                    "uploading",
                    "processing",
                    "ready",
                    "error",
                ]
                assert isinstance(status_data["progress"], int)
                assert 0 <= status_data["progress"] <= 100

            finally:
                app.dependency_overrides.clear()


class TestChatEndpointsContract:
    """Test chat endpoints against API contract"""

    def test_send_message_endpoint_contract(
        self, test_user_in_db, test_access_token, test_project
    ):
        """Test POST /chat/{project_id}/message endpoint contract compliance"""
        app.dependency_overrides[verify_token] = mock_verify_token

        # Mock project service and LangChain service
        with (
            patch("api.chat.project_service") as mock_proj_service,
            patch("api.chat.langchain_service") as mock_lang_service,
        ):

            mock_proj_service.check_project_ownership.return_value = True

            # Mock LangChain service response
            from models.response_schemas import QueryResult

            mock_lang_service.process_query.return_value = QueryResult(
                id="test_query_123",
                query="Test query",
                sql_query="SELECT * FROM data LIMIT 5",
                result_type="table",
                data=[{"col1": "value1", "col2": "value2"}],
                execution_time=0.5,
                row_count=1,
                chart_config=None,
                error=None,
                summary=None,
            )

            try:
                response = client.post(
                    f"/chat/{test_project.id}/message",
                    json={"message": "Show me the data"},
                    headers={"Authorization": f"Bearer {test_access_token}"},
                )

                assert response.status_code == 200
                data = response.json()

                # Validate ApiResponse structure
                validate_api_response_structure(data)

                # Validate SendMessageResponse structure
                message_response = data["data"]
                required_fields = ["message", "result"]
                optional_fields = ["ai_message"]

                for field in required_fields:
                    assert (
                        field in message_response
                    ), f"SendMessageResponse must have field: {field}"

                # Validate ChatMessage structure
                validate_chat_message_structure(message_response["message"])

                # Validate QueryResult structure
                validate_query_result_structure(message_response["result"])

            finally:
                app.dependency_overrides.clear()

    def test_get_messages_endpoint_contract(
        self, test_user_in_db, test_access_token, test_project
    ):
        """Test GET /chat/{project_id}/messages endpoint contract compliance"""
        app.dependency_overrides[verify_token] = mock_verify_token

        # Mock project service
        with patch("api.chat.project_service") as mock_proj_service:
            mock_proj_service.check_project_ownership.return_value = True

            try:
                response = client.get(
                    f"/chat/{test_project.id}/messages?page=1&limit=20",
                    headers={"Authorization": f"Bearer {test_access_token}"},
                )

                assert response.status_code == 200
                data = response.json()

                # Validate ApiResponse structure
                validate_api_response_structure(data)

                # Validate PaginatedResponse structure
                validate_pagination_response(data["data"])

                # Validate ChatMessage structures in items
                for message in data["data"]["items"]:
                    validate_chat_message_structure(message)

            finally:
                app.dependency_overrides.clear()

    def test_csv_preview_endpoint_contract(
        self, test_user_in_db, test_access_token, test_project
    ):
        """Test GET /chat/{project_id}/preview endpoint contract compliance"""
        app.dependency_overrides[verify_token] = mock_verify_token

        # Mock project service
        with patch("api.chat.project_service") as mock_proj_service:
            mock_proj_service.check_project_ownership.return_value = True
            mock_proj_service.get_project_by_id.return_value = Mock(
                id=test_project.id,
                user_id=test_user_in_db.id,
                csv_path="test/path/data.csv",
                columns_metadata=[
                    {
                        "name": "test_column",
                        "type": "string",
                        "sample_values": ["value1", "value2", "value3"],
                    }
                ],
                row_count=100,
            )

            # Mock storage service to prevent MinIO connection
            with patch("services.storage_service.storage_service") as mock_storage:
                mock_storage.download_file.return_value = (
                    None  # Simulate file not found
                )

                try:
                    response = client.get(
                        f"/chat/{test_project.id}/preview",
                        headers={"Authorization": f"Bearer {test_access_token}"},
                    )

                    assert response.status_code == 200
                    data = response.json()

                    # Validate ApiResponse structure
                    validate_api_response_structure(data)

                    # Validate CSVPreview structure
                    preview_data = data["data"]
                    required_fields = [
                        "columns",
                        "sample_data",
                        "total_rows",
                        "data_types",
                    ]

                    for field in required_fields:
                        assert (
                            field in preview_data
                        ), f"CSVPreview must have field: {field}"

                    # Validate field types
                    assert isinstance(preview_data["columns"], list)
                    assert isinstance(preview_data["sample_data"], list)
                    assert isinstance(preview_data["total_rows"], int)
                    assert isinstance(preview_data["data_types"], dict)

                finally:
                    app.dependency_overrides.clear()

    def test_suggestions_endpoint_contract(
        self, test_user_in_db, test_access_token, test_project
    ):
        """Test GET /chat/{project_id}/suggestions endpoint contract compliance"""
        app.dependency_overrides[verify_token] = mock_verify_token

        # Mock project service and LangChain service
        with (
            patch("api.chat.project_service") as mock_proj_service,
            patch("api.chat.langchain_service") as mock_lang_service,
        ):

            mock_proj_service.check_project_ownership.return_value = True

            # Mock suggestions response
            mock_lang_service.generate_suggestions.return_value = [
                {
                    "id": "sug_001",
                    "text": "Show me total sales",
                    "category": "analysis",
                    "complexity": "beginner",
                }
            ]

            try:
                response = client.get(
                    f"/chat/{test_project.id}/suggestions",
                    headers={"Authorization": f"Bearer {test_access_token}"},
                )

                assert response.status_code == 200
                data = response.json()

                # Validate ApiResponse structure
                validate_api_response_structure(data)

                # Validate QuerySuggestion structures
                suggestions = data["data"]
                assert isinstance(suggestions, list)

                for suggestion in suggestions:
                    validate_query_suggestion_structure(suggestion)

            finally:
                app.dependency_overrides.clear()


class TestHealthEndpointsContract:
    """Test health endpoints against API contract"""

    def test_health_endpoint_contract(self):
        """Test GET /health endpoint contract compliance"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        # Validate ApiResponse structure
        validate_api_response_structure(data)

        # Validate HealthStatus structure
        health_data = data["data"]
        required_fields = ["status", "service", "version", "timestamp", "checks"]

        for field in required_fields:
            assert field in health_data, f"HealthStatus must have field: {field}"

        # Validate status enum
        assert health_data["status"] in ["healthy", "unhealthy"]

        # Validate checks structure
        checks = health_data["checks"]
        required_check_fields = ["database", "redis", "storage", "llm_service"]

        for field in required_check_fields:
            assert field in checks, f"HealthStatus.checks must have field: {field}"
            assert isinstance(checks[field], bool), f"checks.{field} must be boolean"

    def test_root_endpoint_contract(self):
        """Test GET / endpoint contract compliance"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        # Validate ApiResponse structure
        validate_api_response_structure(data)

        # Validate root response structure
        root_data = data["data"]
        required_fields = ["message", "status"]

        for field in required_fields:
            assert field in root_data, f"Root response must have field: {field}"
            assert isinstance(root_data[field], str), f"{field} must be string"


# Helper validation functions


def validate_chat_message_structure(message_data: Dict[str, Any]) -> None:
    """Validate ChatMessage structure against API contract"""
    required_fields = ["id", "project_id", "user_id", "content", "role", "created_at"]
    optional_fields = ["metadata"]

    for field in required_fields:
        assert field in message_data, f"ChatMessage must have field: {field}"

    # Validate role enum
    assert message_data["role"] in [
        "user",
        "assistant",
    ], f"Invalid role: {message_data['role']}"


def validate_query_result_structure(result_data: Dict[str, Any]) -> None:
    """Validate QueryResult structure against API contract"""
    required_fields = ["id", "query", "result_type", "execution_time"]
    optional_fields = [
        "sql_query",
        "data",
        "chart_config",
        "summary",
        "error",
        "row_count",
    ]

    for field in required_fields:
        assert field in result_data, f"QueryResult must have field: {field}"

    # Validate result_type enum
    valid_types = ["table", "chart", "summary", "error"]
    assert (
        result_data["result_type"] in valid_types
    ), f"Invalid result_type: {result_data['result_type']}"

    # Validate execution_time is numeric
    assert isinstance(
        result_data["execution_time"], (int, float)
    ), "execution_time must be numeric"


def validate_query_suggestion_structure(suggestion_data: Dict[str, Any]) -> None:
    """Validate QuerySuggestion structure against API contract"""
    required_fields = ["id", "text", "category", "complexity"]

    for field in required_fields:
        assert field in suggestion_data, f"QuerySuggestion must have field: {field}"

    # Validate category enum
    valid_categories = ["analysis", "visualization", "summary", "filter"]
    assert (
        suggestion_data["category"] in valid_categories
    ), f"Invalid category: {suggestion_data['category']}"

    # Validate complexity enum
    valid_complexities = ["beginner", "intermediate", "advanced"]
    assert (
        suggestion_data["complexity"] in valid_complexities
    ), f"Invalid complexity: {suggestion_data['complexity']}"
