import uuid
from datetime import datetime

import pytest

from models.user import (
    GoogleOAuthData,
    UserCreate,
    UserInDB,
    UserPublic,
    UserUpdate,
)


class TestUserServiceModels:
    """Test suite for User models and basic validation"""

    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for testing"""
        return UserCreate(
            email="test@example.com",
            name="Test User",
            avatar_url="https://example.com/avatar.jpg",
            google_id="google_123",
        )

    @pytest.fixture
    def sample_google_data(self):
        """Sample Google OAuth data"""
        return GoogleOAuthData(
            google_id="google_123",
            email="test@example.com",
            name="Test User",
            avatar_url="https://example.com/avatar.jpg",
            email_verified=True,
        )

    @pytest.fixture
    def sample_user_in_db(self):
        """Sample UserInDB instance"""
        return UserInDB(
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

    def test_user_create_validation(self):
        """Test UserCreate model validation"""
        # Valid user creation
        user = UserCreate(
            email="test@example.com",
            name="Test User",
            avatar_url="https://example.com/avatar.jpg",
            google_id="google_123",
        )
        assert user.email == "test@example.com"
        assert user.name == "Test User"

        # Test with minimal data
        minimal_user = UserCreate(
            email="minimal@example.com",
            name="Minimal User",
        )
        assert minimal_user.avatar_url is None
        assert minimal_user.google_id is None

    def test_user_create_email_validation(self):
        """Test email validation in UserCreate"""
        with pytest.raises(ValueError):
            UserCreate(
                email="invalid-email",
                name="Test User",
            )

    def test_user_create_name_validation(self):
        """Test name validation in UserCreate"""
        with pytest.raises(ValueError):
            UserCreate(
                email="test@example.com",
                name="",
            )

        with pytest.raises(ValueError):
            UserCreate(
                email="test@example.com",
                name="   ",
            )

        # Test name trimming
        user = UserCreate(
            email="test@example.com",
            name="  Test User  ",
        )
        assert user.name == "Test User"

    def test_user_create_avatar_url_validation(self):
        """Test avatar URL validation"""
        with pytest.raises(ValueError):
            UserCreate(
                email="test@example.com",
                name="Test User",
                avatar_url="invalid-url",
            )

        # Valid URLs should work
        user = UserCreate(
            email="test@example.com",
            name="Test User",
            avatar_url="https://example.com/avatar.jpg",
        )
        assert user.avatar_url == "https://example.com/avatar.jpg"

    def test_user_update_model(self):
        """Test UserUpdate model"""
        # Test partial update
        update = UserUpdate(name="Updated Name")
        assert update.name == "Updated Name"
        assert update.avatar_url is None

        # Test full update
        full_update = UserUpdate(
            name="Updated Name",
            avatar_url="https://example.com/new-avatar.jpg",
            is_active=False,
            is_verified=True,
            last_sign_in_at=datetime.utcnow(),
        )
        assert full_update.name == "Updated Name"
        assert full_update.is_active is False

    def test_user_in_db_model(self, sample_user_in_db):
        """Test UserInDB model"""
        assert isinstance(sample_user_in_db.id, uuid.UUID)
        assert sample_user_in_db.email == "test@example.com"
        assert sample_user_in_db.is_active is True
        assert isinstance(sample_user_in_db.created_at, datetime)

    def test_user_public_conversion(self, sample_user_in_db):
        """Test UserPublic conversion from UserInDB"""
        public_user = UserPublic.from_db_user(sample_user_in_db)

        assert isinstance(public_user.id, str)
        assert public_user.email == sample_user_in_db.email
        assert public_user.name == sample_user_in_db.name
        assert public_user.created_at.endswith("Z")

    def test_google_oauth_data_validation(self):
        """Test GoogleOAuthData validation"""
        # Valid Google OAuth data
        oauth_data = GoogleOAuthData(
            google_id="google_123",
            email="test@example.com",
            name="Test User",
            avatar_url="https://example.com/avatar.jpg",
            email_verified=True,
        )
        assert oauth_data.google_id == "google_123"
        assert oauth_data.email_verified is True

    def test_google_oauth_empty_google_id(self):
        """Test GoogleOAuthData with empty Google ID"""
        with pytest.raises(ValueError):
            GoogleOAuthData(
                google_id="",
                email="test@example.com",
                name="Test User",
            )

        with pytest.raises(ValueError):
            GoogleOAuthData(
                google_id="   ",
                email="test@example.com",
                name="Test User",
            )

    def test_google_oauth_whitespace_trimming(self):
        """Test GoogleOAuthData trims whitespace from Google ID"""
        oauth_data = GoogleOAuthData(
            google_id="  google_123  ",
            email="test@example.com",
            name="Test User",
        )
        assert oauth_data.google_id == "google_123"


class TestUserServiceLogic:
    """Test UserService business logic (without database)"""

    def test_user_service_import(self):
        """Test that UserService can be imported and instantiated"""
        from services.user_service import UserService

        service = UserService()
        assert service is not None

    def test_health_check_method_exists(self):
        """Test that health_check method exists"""
        from services.user_service import UserService

        service = UserService()
        assert hasattr(service, "health_check")
        assert callable(getattr(service, "health_check"))
