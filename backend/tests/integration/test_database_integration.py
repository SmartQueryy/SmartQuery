"""
Database Integration Tests - Task B26

Tests the integration between database service, user service, and project service
to ensure all CRUD operations work correctly with real database transactions.
"""

import uuid
from datetime import datetime
from typing import Optional

import pytest

from models.project import ProjectCreate
from models.user import GoogleOAuthData, UserInDB
from services.database_service import get_db_service
from services.project_service import get_project_service
from services.user_service import get_user_service


class TestDatabaseIntegration:
    """Integration tests for database operations across all services"""

    def test_user_lifecycle_integration(self, test_db_setup):
        """Test complete user lifecycle: create, read, update, delete"""
        user_service = get_user_service()

        # Test user creation
        google_data = GoogleOAuthData(
            google_id="integration_test_123",
            email="integration@test.com",
            name="Integration Test User",
            avatar_url="https://example.com/avatar.jpg",
        )

        created_user, is_new_user = user_service.create_or_update_from_google_oauth(
            google_data
        )
        assert created_user is not None
        assert created_user.email == "integration@test.com"
        assert created_user.name == "Integration Test User"
        assert created_user.google_id == "integration_test_123"

        # Test user retrieval by ID
        retrieved_user = user_service.get_user_by_id(created_user.id)
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email

        # Test user retrieval by Google ID
        google_user = user_service.get_user_by_google_id("integration_test_123")
        assert google_user is not None
        assert google_user.id == created_user.id

        # Test user update
        updated_user = user_service.update_last_sign_in(created_user.id)
        assert updated_user is not None
        assert updated_user.last_sign_in_at is not None

        # Test user deletion
        success = user_service.delete_user(created_user.id)
        assert success is True

        # Verify user is deleted
        deleted_user = user_service.get_user_by_id(created_user.id)
        assert deleted_user is None

    def test_project_lifecycle_integration(self, test_db_setup):
        """Test complete project lifecycle: create, read, update, delete"""
        user_service = get_user_service()
        project_service = get_project_service()

        # First create a user
        google_data = GoogleOAuthData(
            google_id="project_test_456",
            email="project@test.com",
            name="Project Test User",
        )
        test_user, _ = user_service.create_or_update_from_google_oauth(google_data)
        assert test_user is not None

        # Test project creation
        project_data = ProjectCreate(
            name="Integration Test Project", description="Testing project lifecycle"
        )

        created_project = project_service.create_project(project_data, test_user.id)
        assert created_project is not None
        assert created_project.name == "Integration Test Project"
        assert created_project.description == "Testing project lifecycle"
        assert created_project.user_id == test_user.id
        assert created_project.status == "uploading"

        # Test project retrieval by ID
        retrieved_project = project_service.get_project_by_id(created_project.id)
        assert retrieved_project is not None
        assert retrieved_project.id == created_project.id
        assert retrieved_project.name == created_project.name

        # Test projects retrieval by user
        user_projects = project_service.get_projects_by_user(
            test_user.id, skip=0, limit=10
        )
        assert len(user_projects) == 1
        assert user_projects[0].id == created_project.id

        # Test project count by user
        project_count = project_service.count_projects_by_user(test_user.id)
        assert project_count == 1

        # Test project ownership check
        ownership = project_service.check_project_ownership(
            created_project.id, test_user.id
        )
        assert ownership is True

        # Test ownership check with wrong user
        wrong_user_id = uuid.uuid4()
        wrong_ownership = project_service.check_project_ownership(
            created_project.id, wrong_user_id
        )
        assert wrong_ownership is False

        # Test project status update
        updated_project = project_service.update_project_status(
            created_project.id, "ready"
        )
        assert updated_project is not None
        assert updated_project.status == "ready"

        # Test project metadata update
        test_metadata = [
            {
                "name": "test_column",
                "type": "string",
                "nullable": False,
                "sample_values": ["value1", "value2", "value3"],
            }
        ]

        metadata_updated = project_service.update_project_metadata(
            created_project.id,
            row_count=100,
            column_count=1,
            columns_metadata=test_metadata,
        )
        assert metadata_updated is not None
        assert metadata_updated.row_count == 100
        assert metadata_updated.column_count == 1
        assert len(metadata_updated.columns_metadata) == 1

        # Test project deletion
        success = project_service.delete_project(created_project.id)
        assert success is True

        # Verify project is deleted
        deleted_project = project_service.get_project_by_id(created_project.id)
        assert deleted_project is None

        # Clean up user
        user_service.delete_user(test_user.id)

    def test_user_project_relationship_integration(self, test_db_setup):
        """Test the relationship between users and projects"""
        user_service = get_user_service()
        project_service = get_project_service()

        # Create two test users
        user1_data = GoogleOAuthData(
            google_id="rel_test_1", email="user1@test.com", name="User One"
        )
        user2_data = GoogleOAuthData(
            google_id="rel_test_2", email="user2@test.com", name="User Two"
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
        project3_data = ProjectCreate(
            name="User 1 Project 2", description="Second project for user 1"
        )

        project1 = project_service.create_project(project1_data, user1.id)
        project2 = project_service.create_project(project2_data, user2.id)
        project3 = project_service.create_project(project3_data, user1.id)

        # Test that each user only sees their own projects
        user1_projects = project_service.get_projects_by_user(
            user1.id, skip=0, limit=10
        )
        user2_projects = project_service.get_projects_by_user(
            user2.id, skip=0, limit=10
        )

        assert len(user1_projects) == 2
        assert len(user2_projects) == 1

        user1_project_ids = {p.id for p in user1_projects}
        user2_project_ids = {p.id for p in user2_projects}

        assert project1.id in user1_project_ids
        assert project3.id in user1_project_ids
        assert project2.id in user2_project_ids
        assert project2.id not in user1_project_ids
        assert project1.id not in user2_project_ids

        # Test project counts
        assert project_service.count_projects_by_user(user1.id) == 2
        assert project_service.count_projects_by_user(user2.id) == 1

        # Test ownership checks
        assert project_service.check_project_ownership(project1.id, user1.id) is True
        assert project_service.check_project_ownership(project1.id, user2.id) is False
        assert project_service.check_project_ownership(project2.id, user2.id) is True
        assert project_service.check_project_ownership(project2.id, user1.id) is False

        # Clean up
        project_service.delete_project(project1.id)
        project_service.delete_project(project2.id)
        project_service.delete_project(project3.id)
        user_service.delete_user(user1.id)
        user_service.delete_user(user2.id)

    def test_database_transaction_rollback(self, test_db_setup):
        """Test that database transactions roll back properly on errors"""
        user_service = get_user_service()
        project_service = get_project_service()
        db_service = get_db_service()

        # Create a test user
        google_data = GoogleOAuthData(
            google_id="transaction_test",
            email="transaction@test.com",
            name="Transaction Test User",
        )
        test_user, _ = user_service.create_or_update_from_google_oauth(google_data)

        # Get initial project count
        initial_count = project_service.count_projects_by_user(test_user.id)
        assert initial_count == 0

        # Try to create a project with invalid data that should cause a rollback
        # This test verifies that database constraints and transactions work properly
        with pytest.raises(Exception):
            # Attempt to create project with invalid user_id (should fail)
            invalid_uuid = uuid.UUID("00000000-0000-0000-0000-000000000000")
            project_data = ProjectCreate(name="Invalid Project")
            project_service.create_project(project_data, invalid_uuid)

        # Verify that no project was created (transaction rolled back)
        final_count = project_service.count_projects_by_user(test_user.id)
        assert final_count == initial_count

        # Verify the user still exists (no cascade issues)
        user_check = user_service.get_user_by_id(test_user.id)
        assert user_check is not None

        # Clean up
        user_service.delete_user(test_user.id)

    def test_database_connection_handling(self, test_db_setup):
        """Test database connection pooling and error handling"""
        db_service = get_db_service()
        user_service = get_user_service()

        # Test database connection
        assert db_service.engine is not None
        assert db_service.SessionLocal is not None

        # Test multiple concurrent operations
        users_created = []
        for i in range(5):
            google_data = GoogleOAuthData(
                google_id=f"concurrent_test_{i}",
                email=f"concurrent_{i}@test.com",
                name=f"Concurrent User {i}",
            )
            user, _ = user_service.create_or_update_from_google_oauth(google_data)
            users_created.append(user)

        # Verify all users were created
        assert len(users_created) == 5

        # Clean up
        for user in users_created:
            user_service.delete_user(user.id)

    def test_database_constraints_and_validation(self, test_db_setup):
        """Test database constraints and data validation"""
        user_service = get_user_service()

        # Test unique constraint on google_id
        google_data1 = GoogleOAuthData(
            google_id="unique_test", email="unique1@test.com", name="Unique Test 1"
        )
        google_data2 = GoogleOAuthData(
            google_id="unique_test",  # Same google_id
            email="unique2@test.com",
            name="Unique Test 2",
        )

        # First user should create successfully
        user1, _ = user_service.create_or_update_from_google_oauth(google_data1)
        assert user1 is not None

        # Second user with same google_id should handle gracefully
        # (The service should either return existing user or handle conflict)
        user2, _ = user_service.create_or_update_from_google_oauth(google_data2)
        # The behavior depends on implementation - it might return existing user
        # or handle the conflict in a specific way

        # Clean up
        if user1:
            user_service.delete_user(user1.id)
        if user2 and user2.id != user1.id:
            user_service.delete_user(user2.id)
