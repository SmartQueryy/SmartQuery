"""
End-to-End Workflow Integration Tests - Task B26

Tests complete user workflows from authentication through project creation,
file upload, processing, and querying to ensure all services work together seamlessly.
"""

import io
import uuid
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from main import app
from middleware.auth_middleware import verify_token
from models.project import ProjectCreate
from models.response_schemas import QueryResult
from models.user import GoogleOAuthData
from services.auth_service import AuthService
from services.project_service import get_project_service
from services.user_service import get_user_service

client = TestClient(app)


def mock_verify_token():
    """Mock verify_token that returns test user UUID"""
    return "00000000-0000-0000-0000-000000000001"


class TestWorkflowIntegration:
    """Integration tests for complete user workflows"""

    def test_complete_user_authentication_workflow(self, test_db_setup):
        """Test complete authentication workflow from login to logout"""
        auth_service = AuthService()
        user_service = get_user_service()

        # Step 1: Simulate Google OAuth login
        google_data = GoogleOAuthData(
            google_id="workflow_auth_test",
            email="workflow@test.com",
            name="Workflow Test User",
            avatar_url="https://example.com/avatar.jpg",
        )

        # Mock Google OAuth validation
        with patch(
            "services.auth_service.AuthService.validate_google_token"
        ) as mock_validate:
            mock_validate.return_value = google_data

            # Step 2: Login and get tokens
            user, access_token, refresh_token, is_new_user = (
                auth_service.login_with_google("mock_token")
            )

            assert user is not None
            assert access_token is not None
            assert refresh_token is not None
            assert user.email == "workflow@test.com"

        # Step 3: Use access token to access protected endpoints
        app.dependency_overrides[verify_token] = lambda: str(user.id)

        try:
            # Test authenticated user endpoint
            with patch("api.auth.auth_service.get_current_user") as mock_get_user:
                mock_get_user.return_value = user

                response = client.get(
                    "/auth/me", headers={"Authorization": f"Bearer {access_token}"}
                )
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["data"]["email"] == "workflow@test.com"

        finally:
            app.dependency_overrides.clear()

        # Step 4: Logout and revoke tokens
        with patch("api.auth.auth_service.revoke_user_tokens") as mock_revoke:
            mock_revoke.return_value = True

            logout_success = auth_service.revoke_user_tokens(user.id)
            assert logout_success is True

        # Clean up
        user_service.delete_user(user.id)

    def test_complete_project_lifecycle_workflow(self, test_db_setup):
        """Test complete project workflow from creation to deletion"""
        user_service = get_user_service()
        project_service = get_project_service()

        # Step 1: Create test user
        google_data = GoogleOAuthData(
            google_id="project_workflow_test",
            email="projectworkflow@test.com",
            name="Project Workflow User",
        )
        test_user, _ = user_service.create_or_update_from_google_oauth(google_data)

        app.dependency_overrides[verify_token] = lambda: str(test_user.id)

        try:
            # Step 2: Create project via API
            response = client.post(
                "/projects",
                json={
                    "name": "Workflow Test Project",
                    "description": "Complete workflow test",
                },
                headers={"Authorization": "Bearer mock_token"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            project_data = data["data"]
            project_id = project_data["project"]["id"]

            # Step 3: Check project status
            response = client.get(
                f"/projects/{project_id}/status",
                headers={"Authorization": "Bearer mock_token"},
            )

            assert response.status_code == 200
            status_data = response.json()
            assert status_data["success"] is True
            assert status_data["data"]["status"] == "uploading"

            # Step 4: Simulate file upload by updating project metadata
            test_metadata = [
                {
                    "name": "name",
                    "type": "string",
                    "nullable": False,
                    "sample_values": ["Alice", "Bob", "Charlie"],
                },
                {
                    "name": "age",
                    "type": "number",
                    "nullable": False,
                    "sample_values": [25, 30, 35],
                },
            ]

            project_uuid = uuid.UUID(project_id)
            project_service.update_project_metadata(
                project_uuid,
                row_count=100,
                column_count=2,
                columns_metadata=test_metadata,
            )
            project_service.update_project_status(project_uuid, "ready")

            # Step 5: Verify project is ready
            response = client.get(
                f"/projects/{project_id}/status",
                headers={"Authorization": "Bearer mock_token"},
            )

            assert response.status_code == 200
            status_data = response.json()
            assert status_data["data"]["status"] == "ready"

            # Step 6: Get project details
            response = client.get(
                f"/projects/{project_id}",
                headers={"Authorization": "Bearer mock_token"},
            )

            assert response.status_code == 200
            project_details = response.json()
            assert project_details["success"] is True
            assert project_details["data"]["row_count"] == 100
            assert len(project_details["data"]["columns_metadata"]) == 2

            # Step 7: Delete project
            response = client.delete(
                f"/projects/{project_id}",
                headers={"Authorization": "Bearer mock_token"},
            )

            assert response.status_code == 200
            delete_response = response.json()
            assert delete_response["success"] is True

            # Step 8: Verify project is deleted
            response = client.get(
                f"/projects/{project_id}",
                headers={"Authorization": "Bearer mock_token"},
            )

            assert response.status_code == 404

        finally:
            app.dependency_overrides.clear()

        # Clean up
        user_service.delete_user(test_user.id)

    @patch("services.langchain_service.ChatOpenAI")
    @patch("services.langchain_service.duckdb_service")
    def test_complete_chat_workflow(
        self, mock_duckdb, mock_openai, test_db_setup
    ):
        """Test complete chat workflow from project creation to querying"""
        user_service = get_user_service()
        project_service = get_project_service()

        # Mock services
        mock_llm = Mock()
        mock_llm.invoke.return_value.content = (
            "SELECT name, age FROM data WHERE age > 25"
        )
        mock_openai.return_value = mock_llm

        mock_duckdb.execute_query.return_value = (
            [{"name": "Bob", "age": 30}, {"name": "Charlie", "age": 35}],
            0.08,
            2
        )
        mock_duckdb.validate_sql_query.return_value = (True, "")

        # Step 1: Create test user and project
        google_data = GoogleOAuthData(
            google_id="chat_workflow_test",
            email="chatworkflow@test.com",
            name="Chat Workflow User",
        )
        test_user, _ = user_service.create_or_update_from_google_oauth(google_data)

        project_data = ProjectCreate(
            name="Chat Workflow Project", description="Testing complete chat workflow"
        )
        test_project = project_service.create_project(project_data, test_user.id)

        # Step 2: Setup project with metadata
        test_metadata = [
            {
                "name": "name",
                "type": "string",
                "nullable": False,
                "sample_values": ["Alice", "Bob", "Charlie", "Diana"],
            },
            {
                "name": "age",
                "type": "number",
                "nullable": False,
                "sample_values": [22, 30, 35, 28],
            },
            {
                "name": "department",
                "type": "string",
                "nullable": False,
                "sample_values": ["Engineering", "Sales", "Marketing", "HR"],
            },
        ]

        project_service.update_project_metadata(
            test_project.id,
            row_count=200,
            column_count=3,
            columns_metadata=test_metadata,
        )
        project_service.update_project_status(test_project.id, "ready")

        app.dependency_overrides[verify_token] = lambda: str(test_user.id)

        try:
            # Step 3: Get CSV preview
            with patch("api.chat.project_service") as mock_proj_service:
                mock_proj_service.check_project_ownership.return_value = True
                mock_proj_service.get_project_by_id.return_value = Mock(
                    id=test_project.id,
                    user_id=test_user.id,
                    csv_path="test/employees.csv",
                    columns_metadata=test_metadata,
                    row_count=200,
                )

                with patch(
                    "services.storage_service.storage_service.download_file",
                    return_value=None,
                ):
                    response = client.get(
                        f"/chat/{test_project.id}/preview",
                        headers={"Authorization": "Bearer mock_token"},
                    )

                    assert response.status_code == 200
                    preview_data = response.json()
                    assert preview_data["success"] is True
                    assert "columns" in preview_data["data"]

            # Step 4: Get query suggestions
            with (
                patch("api.chat.project_service") as mock_proj_service,
                patch("api.chat.langchain_service") as mock_lang_service,
            ):

                mock_proj_service.check_project_ownership.return_value = True
                mock_lang_service.generate_suggestions.return_value = [
                    {
                        "id": "sug_001",
                        "text": "Show me employees older than 25",
                        "category": "analysis",
                        "complexity": "beginner",
                    },
                    {
                        "id": "sug_002",
                        "text": "Group employees by department",
                        "category": "analysis",
                        "complexity": "intermediate",
                    },
                ]

                response = client.get(
                    f"/chat/{test_project.id}/suggestions",
                    headers={"Authorization": "Bearer mock_token"},
                )

                assert response.status_code == 200
                suggestions_data = response.json()
                assert suggestions_data["success"] is True
                assert len(suggestions_data["data"]) == 2

            # Step 5: Send chat message and get response
            with (
                patch("api.chat.project_service") as mock_proj_service,
                patch("api.chat.langchain_service") as mock_lang_service,
            ):

                mock_proj_service.check_project_ownership.return_value = True

                mock_query_result = QueryResult(
                    id="query_001",
                    query="Show me employees older than 25",
                    sql_query="SELECT name, age FROM data WHERE age > 25",
                    result_type="table",
                    data=[{"name": "Bob", "age": 30}, {"name": "Charlie", "age": 35}],
                    execution_time=0.08,
                    row_count=2,
                    chart_config=None,
                    error=None,
                    summary=None,
                )

                mock_lang_service.process_query.return_value = mock_query_result

                response = client.post(
                    f"/chat/{test_project.id}/message",
                    json={"message": "Show me employees older than 25"},
                    headers={"Authorization": "Bearer mock_token"},
                )

                assert response.status_code == 200
                chat_data = response.json()
                assert chat_data["success"] is True
                assert "message" in chat_data["data"]
                assert "result" in chat_data["data"]
                assert chat_data["data"]["result"]["result_type"] == "table"
                assert chat_data["data"]["result"]["row_count"] == 2

            # Step 6: Get chat message history
            with patch("api.chat.project_service") as mock_proj_service:
                mock_proj_service.check_project_ownership.return_value = True

                response = client.get(
                    f"/chat/{test_project.id}/messages?page=1&limit=20",
                    headers={"Authorization": "Bearer mock_token"},
                )

                assert response.status_code == 200
                messages_data = response.json()
                assert messages_data["success"] is True
                assert "items" in messages_data["data"]
                assert "total" in messages_data["data"]

        finally:
            app.dependency_overrides.clear()

        # Clean up
        project_service.delete_project(test_project.id)
        user_service.delete_user(test_user.id)

    def test_multi_user_workflow_isolation(self, test_db_setup):
        """Test that workflows are properly isolated between different users"""
        user_service = get_user_service()
        project_service = get_project_service()

        # Create two test users
        user1_data = GoogleOAuthData(
            google_id="isolation_user_1", email="user1@test.com", name="User One"
        )
        user2_data = GoogleOAuthData(
            google_id="isolation_user_2", email="user2@test.com", name="User Two"
        )

        user1, _ = user_service.create_or_update_from_google_oauth(user1_data)
        user2, _ = user_service.create_or_update_from_google_oauth(user2_data)

        # Create projects for each user
        project1_data = ProjectCreate(
            name="User 1 Project", description="Project for user 1"
        )
        project2_data = ProjectCreate(
            name="User 2 Project", description="Project for user 2"
        )

        project1 = project_service.create_project(project1_data, user1.id)
        project2 = project_service.create_project(project2_data, user2.id)

        # Test User 1 workflow
        app.dependency_overrides[verify_token] = lambda: str(user1.id)

        try:
            # User 1 can access their own project
            response = client.get(
                f"/projects/{project1.id}",
                headers={"Authorization": "Bearer mock_token"},
            )
            assert response.status_code == 200

            # User 1 cannot access User 2's project
            response = client.get(
                f"/projects/{project2.id}",
                headers={"Authorization": "Bearer mock_token"},
            )
            assert response.status_code == 403

            # User 1 sees only their projects in list
            response = client.get(
                "/projects?page=1&limit=20",
                headers={"Authorization": "Bearer mock_token"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]["items"]) == 1
            assert data["data"]["items"][0]["id"] == str(project1.id)

        finally:
            app.dependency_overrides.clear()

        # Test User 2 workflow
        app.dependency_overrides[verify_token] = lambda: str(user2.id)

        try:
            # User 2 can access their own project
            response = client.get(
                f"/projects/{project2.id}",
                headers={"Authorization": "Bearer mock_token"},
            )
            assert response.status_code == 200

            # User 2 cannot access User 1's project
            response = client.get(
                f"/projects/{project1.id}",
                headers={"Authorization": "Bearer mock_token"},
            )
            assert response.status_code == 403

            # User 2 sees only their projects in list
            response = client.get(
                "/projects?page=1&limit=20",
                headers={"Authorization": "Bearer mock_token"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]["items"]) == 1
            assert data["data"]["items"][0]["id"] == str(project2.id)

        finally:
            app.dependency_overrides.clear()

        # Clean up
        project_service.delete_project(project1.id)
        project_service.delete_project(project2.id)
        user_service.delete_user(user1.id)
        user_service.delete_user(user2.id)

    def test_error_recovery_workflow(self, test_db_setup):
        """Test error handling and recovery in complete workflows"""
        user_service = get_user_service()
        project_service = get_project_service()

        # Create test user
        google_data = GoogleOAuthData(
            google_id="error_recovery_test",
            email="errorrecovery@test.com",
            name="Error Recovery User",
        )
        test_user, _ = user_service.create_or_update_from_google_oauth(google_data)

        app.dependency_overrides[verify_token] = lambda: str(test_user.id)

        try:
            # Test handling of invalid project ID
            response = client.get(
                "/projects/invalid-uuid", headers={"Authorization": "Bearer mock_token"}
            )
            assert response.status_code == 400
            error_data = response.json()
            assert error_data["success"] is False
            assert "error" in error_data

            # Test handling of non-existent project
            fake_uuid = str(uuid.uuid4())
            response = client.get(
                f"/projects/{fake_uuid}", headers={"Authorization": "Bearer mock_token"}
            )
            assert response.status_code == 404
            error_data = response.json()
            assert error_data["success"] is False

            # Test handling of malformed request data
            response = client.post(
                "/projects",
                json={"invalid_field": "invalid_data"},  # Missing required name field
                headers={"Authorization": "Bearer mock_token"},
            )
            assert response.status_code == 422

            # Test recovery after error - normal operation should still work
            response = client.post(
                "/projects",
                json={
                    "name": "Recovery Test Project",
                    "description": "Testing error recovery",
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

            # Clean up the created project
            project_id = data["data"]["project"]["id"]
            client.delete(
                f"/projects/{project_id}",
                headers={"Authorization": "Bearer mock_token"},
            )

        finally:
            app.dependency_overrides.clear()

        # Clean up
        user_service.delete_user(test_user.id)

    def test_system_health_workflow(self, test_db_setup):
        """Test system health checking workflow"""
        # Test system health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        health_data = response.json()

        assert health_data["success"] is True
        assert "status" in health_data["data"]
        assert "service" in health_data["data"]
        assert "checks" in health_data["data"]

        health_checks = health_data["data"]["checks"]
        assert "database" in health_checks
        assert "redis" in health_checks
        assert "storage" in health_checks
        assert "llm_service" in health_checks

        # Test root endpoint
        response = client.get("/")
        assert response.status_code == 200
        root_data = response.json()

        assert root_data["success"] is True
        assert "message" in root_data["data"]
        assert "status" in root_data["data"]
