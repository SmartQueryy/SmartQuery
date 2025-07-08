import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from models.user import (
    GoogleOAuthData,
    UserCreate,
    UserInDB,
    UserTable,
    UserUpdate,
)
from services.user_service import UserService
from unittest.mock import MagicMock, patch


class TestUserServiceModels:
    """Test suite for Pydantic models related to UserService"""

    def test_user_create_validation(self):
        """Test UserCreate model validation"""
        # Valid data
        user_data = UserCreate(
            email="test@example.com", name="Test User", google_id="12345"
        )
        assert user_data.name == "Test User"

        # Minimal data
        minimal_user = UserCreate(
            email="minimal@example.com", name="Minimal User", google_id="54321"
        )
        assert minimal_user.avatar_url is None

    def test_user_create_email_validation(self):
        """Test email validation in UserCreate"""
        with pytest.raises(ValidationError):
            UserCreate(email="not-an-email", name="Test", google_id="123")

    def test_user_create_name_validation(self):
        """Test name validation in UserCreate"""
        with pytest.raises(ValidationError):
            UserCreate(email="test@example.com", name="", google_id="123")

        user = UserCreate(
            email="test@example.com", name="  Test User  ", google_id="123"
        )
        assert user.name == "Test User"

    def test_user_create_avatar_url_validation(self):
        """Test avatar URL validation in UserCreate"""
        user = UserCreate(
            email="test@example.com",
            name="Test",
            google_id="123",
            avatar_url="http://example.com/avatar.jpg",
        )
        assert user.avatar_url == "http://example.com/avatar.jpg"

    def test_user_update_model(self):
        """Test UserUpdate model"""
        update = UserUpdate(name="New Name", avatar_url="http://new.url/img.png")
        assert update.name == "New Name"
        assert "is_active" not in update.model_dump()

    def test_user_in_db_model(self):
        """Test UserInDB model creation from ORM object"""
        user_table = UserTable(
            id=uuid.uuid4(),
            email="db@example.com",
            name="DB User",
            is_active=True,
            is_verified=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        user_in_db = UserInDB.model_validate(user_table)
        assert user_in_db.name == "DB User"

    def test_google_oauth_data_validation(self):
        """Test GoogleOAuthData validation"""
        oauth_data = GoogleOAuthData(
            google_id="google123",
            email="oauth@example.com",
            name="OAuth User",
        )
        assert oauth_data.name == "OAuth User"
        assert oauth_data.google_id == "google123"

    def test_google_oauth_empty_google_id(self):
        """Test GoogleOAuthData with empty Google ID"""
        with pytest.raises(ValidationError):
            GoogleOAuthData(google_id="", email="test@test.com", name="Test")

    def test_google_oauth_whitespace_trimming(self):
        """Test GoogleOAuthData trims whitespace from fields"""
        # This behavior is default in Pydantic v2 unless annotated otherwise
        data = GoogleOAuthData(
            google_id="  google_123  ",
            email=" trim@example.com ",
            name="  Trimmed Name  ",
        )
        assert data.google_id == "google_123"
        assert data.email == "trim@example.com"
        assert data.name == "Trimmed Name"


class TestUserServiceLogic:
    """Test suite for the logic within UserService"""

    @pytest.fixture
    def mock_db_service(self):
        """Mock the database service for testing UserService logic"""
        mock_session = MagicMock()
        mock_db_service = MagicMock()
        mock_db_service.get_session.return_value.__enter__.return_value = mock_session
        return mock_db_service

    def test_user_service_import(self):
        """Test that UserService can be imported and instantiated"""
        service = UserService()
        assert service is not None

    def test_health_check_method_exists(self):
        """Test that health_check method exists"""
        service = UserService()
        assert hasattr(service, "health_check")
        assert callable(getattr(service, "health_check"))
