import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError

from models.user import (
    GoogleOAuthData,
    UserCreate,
    UserInDB,
    UserPublic,
    UserUpdate,
)


class TestUserModels:
    """Test suite for User Pydantic models"""

    def test_user_create_valid(self):
        """Test creating valid UserCreate model"""
        user_data = UserCreate(
            email="test@example.com",
            name="Test User",
            avatar_url="https://example.com/avatar.jpg",
            google_id="google_123",
        )

        assert user_data.email == "test@example.com"
        assert user_data.name == "Test User"
        assert user_data.avatar_url == "https://example.com/avatar.jpg"
        assert user_data.google_id == "google_123"

    def test_user_create_minimal(self):
        """Test creating UserCreate with minimal data"""
        user_data = UserCreate(
            email="minimal@example.com",
            name="Minimal User",
        )

        assert user_data.email == "minimal@example.com"
        assert user_data.name == "Minimal User"
        assert user_data.avatar_url is None
        assert user_data.google_id is None

    def test_user_create_invalid_email(self):
        """Test UserCreate with invalid email"""
        with pytest.raises(ValidationError):
            UserCreate(
                email="invalid-email",
                name="Test User",
            )

    def test_user_create_empty_name(self):
        """Test UserCreate with empty name"""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                name="",
            )

    def test_user_create_invalid_avatar_url(self):
        """Test UserCreate with invalid avatar URL"""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                name="Test User",
                avatar_url="not-a-url",
            )

    def test_user_create_name_whitespace(self):
        """Test UserCreate trims whitespace from name"""
        user_data = UserCreate(
            email="test@example.com",
            name="  Test User  ",
        )
        assert user_data.name == "Test User"

    def test_user_update_valid(self):
        """Test creating valid UserUpdate model"""
        update_data = UserUpdate(
            name="Updated Name",
            avatar_url="https://example.com/new-avatar.jpg",
            is_active=False,
            is_verified=True,
            last_sign_in_at=datetime.now(),
        )

        assert update_data.name == "Updated Name"
        assert update_data.avatar_url == "https://example.com/new-avatar.jpg"
        assert update_data.is_active is False
        assert update_data.is_verified is True
        assert isinstance(update_data.last_sign_in_at, datetime)

    def test_user_update_partial(self):
        """Test UserUpdate with partial data"""
        update_data = UserUpdate(name="Partial Update")

        assert update_data.name == "Partial Update"
        assert update_data.avatar_url is None
        assert update_data.is_active is None

    def test_user_in_db_model(self):
        """Test UserInDB model creation"""
        user_id = uuid.uuid4()
        created_at = datetime.now()
        updated_at = datetime.now()

        user_db = UserInDB(
            id=user_id,
            email="db@example.com",
            name="DB User",
            avatar_url="https://example.com/avatar.jpg",
            google_id="google_db_123",
            is_active=True,
            is_verified=True,
            created_at=created_at,
            updated_at=updated_at,
            last_sign_in_at=None,
        )

        assert user_db.id == user_id
        assert user_db.email == "db@example.com"
        assert user_db.name == "DB User"
        assert user_db.is_active is True
        assert user_db.is_verified is True
        assert user_db.created_at == created_at
        assert user_db.updated_at == updated_at

    def test_user_public_from_db_user(self):
        """Test converting UserInDB to UserPublic"""
        user_id = uuid.uuid4()
        created_at = datetime.now()

        user_db = UserInDB(
            id=user_id,
            email="public@example.com",
            name="Public User",
            avatar_url="https://example.com/avatar.jpg",
            google_id="google_public_123",
            is_active=True,
            is_verified=True,
            created_at=created_at,
            updated_at=created_at,
            last_sign_in_at=created_at,
        )

        public_user = UserPublic.from_db_user(user_db)

        assert public_user.id == str(user_id)
        assert public_user.email == "public@example.com"
        assert public_user.name == "Public User"
        assert public_user.avatar_url == "https://example.com/avatar.jpg"
        assert public_user.created_at == created_at.isoformat() + "Z"
        assert public_user.last_sign_in_at == created_at.isoformat() + "Z"
        # Should not expose sensitive fields
        assert not hasattr(public_user, "google_id")
        assert not hasattr(public_user, "is_active")
        assert not hasattr(public_user, "is_verified")

    def test_google_oauth_data_valid(self):
        """Test valid GoogleOAuthData model"""
        google_data = GoogleOAuthData(
            google_id="google_oauth_123",
            email="oauth@example.com",
            name="OAuth User",
            avatar_url="https://example.com/oauth-avatar.jpg",
            email_verified=True,
        )

        assert google_data.google_id == "google_oauth_123"
        assert google_data.email == "oauth@example.com"
        assert google_data.name == "OAuth User"
        assert google_data.avatar_url == "https://example.com/oauth-avatar.jpg"
        assert google_data.email_verified is True

    def test_google_oauth_data_empty_google_id(self):
        """Test GoogleOAuthData with empty Google ID"""
        with pytest.raises(ValidationError):
            GoogleOAuthData(
                google_id="",
                email="oauth@example.com",
                name="OAuth User",
            )

    def test_google_oauth_data_minimal(self):
        """Test GoogleOAuthData with minimal data"""
        google_data = GoogleOAuthData(
            google_id="minimal_google_123",
            email="minimal@example.com",
            name="Minimal OAuth User",
        )

        assert google_data.google_id == "minimal_google_123"
        assert google_data.email == "minimal@example.com"
        assert google_data.name == "Minimal OAuth User"
        assert google_data.avatar_url is None
        assert google_data.email_verified is False  # Default value

    def test_google_oauth_data_whitespace_google_id(self):
        """Test GoogleOAuthData trims whitespace from Google ID"""
        google_data = GoogleOAuthData(
            google_id="  google_trimmed_123  ",
            email="trim@example.com",
            name="Trim User",
        )
        assert google_data.google_id == "google_trimmed_123"
