import uuid
from datetime import datetime

import pytest
from sqlalchemy import String, create_engine
from sqlalchemy.orm import sessionmaker

from models.user import (
    Base,
    GoogleOAuthData,
    UserCreate,
    UserInDB,
    UserPublic,
    UserTable,
    UserUpdate,
)
from services.user_service import UserService


class TestUserService:
    """Test suite for UserService"""

    @pytest.fixture(scope="function")
    def db_session(self):
        """Create test database session"""
        # Use in-memory SQLite for tests
        engine = create_engine("sqlite:///:memory:")

        # For SQLite, replace UUID with String
        UserTable.id.type = String(36)

        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()

        yield session

        session.close()

    @pytest.fixture
    def user_service(self, db_session):
        """User service with test database"""
        service = UserService()
        # Mock the database service to use our test session
        service.db_service.get_session = lambda: db_session
        return service

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

    def test_create_user_success(self, user_service, sample_user_data):
        """Test successful user creation"""
        user = user_service.create_user(sample_user_data)

        assert isinstance(user, UserInDB)
        assert user.email == sample_user_data.email
        assert user.name == sample_user_data.name
        assert user.avatar_url == sample_user_data.avatar_url
        assert user.google_id == sample_user_data.google_id
        assert user.is_active is True
        assert user.is_verified is True  # Should be True for Google users
        assert isinstance(user.id, uuid.UUID)
        assert isinstance(user.created_at, datetime)

    def test_create_user_duplicate_email(self, user_service, sample_user_data):
        """Test creating user with duplicate email fails"""
        # Create first user
        user_service.create_user(sample_user_data)

        # Try to create another user with same email
        duplicate_data = UserCreate(
            email=sample_user_data.email,
            name="Another User",
            google_id="different_google_id",
        )

        with pytest.raises(ValueError, match="already exists"):
            user_service.create_user(duplicate_data)

    def test_get_user_by_id(self, user_service, sample_user_data):
        """Test getting user by ID"""
        created_user = user_service.create_user(sample_user_data)
        retrieved_user = user_service.get_user_by_id(created_user.id)

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email

    def test_get_user_by_id_not_found(self, user_service):
        """Test getting non-existent user returns None"""
        non_existent_id = uuid.uuid4()
        user = user_service.get_user_by_id(non_existent_id)
        assert user is None

    def test_get_user_by_email(self, user_service, sample_user_data):
        """Test getting user by email"""
        created_user = user_service.create_user(sample_user_data)
        retrieved_user = user_service.get_user_by_email(sample_user_data.email)

        assert retrieved_user is not None
        assert retrieved_user.email == created_user.email
        assert retrieved_user.id == created_user.id

    def test_get_user_by_google_id(self, user_service, sample_user_data):
        """Test getting user by Google ID"""
        created_user = user_service.create_user(sample_user_data)
        retrieved_user = user_service.get_user_by_google_id(sample_user_data.google_id)

        assert retrieved_user is not None
        assert retrieved_user.google_id == created_user.google_id
        assert retrieved_user.id == created_user.id

    def test_update_user(self, user_service, sample_user_data):
        """Test updating user information"""
        created_user = user_service.create_user(sample_user_data)

        update_data = UserUpdate(
            name="Updated Name",
            avatar_url="https://example.com/new-avatar.jpg",
            is_verified=True,
        )

        updated_user = user_service.update_user(created_user.id, update_data)

        assert updated_user.name == "Updated Name"
        assert updated_user.avatar_url == "https://example.com/new-avatar.jpg"
        assert updated_user.is_verified is True
        assert updated_user.email == created_user.email  # Unchanged

    def test_update_last_sign_in(self, user_service, sample_user_data):
        """Test updating last sign-in timestamp"""
        created_user = user_service.create_user(sample_user_data)
        assert created_user.last_sign_in_at is None

        updated_user = user_service.update_last_sign_in(created_user.id)
        assert updated_user.last_sign_in_at is not None
        assert isinstance(updated_user.last_sign_in_at, datetime)

    def test_deactivate_user(self, user_service, sample_user_data):
        """Test deactivating user"""
        created_user = user_service.create_user(sample_user_data)
        assert created_user.is_active is True

        deactivated_user = user_service.deactivate_user(created_user.id)
        assert deactivated_user.is_active is False

    def test_activate_user(self, user_service, sample_user_data):
        """Test activating user"""
        created_user = user_service.create_user(sample_user_data)
        user_service.deactivate_user(created_user.id)

        activated_user = user_service.activate_user(created_user.id)
        assert activated_user.is_active is True

    def test_verify_user_email(self, user_service):
        """Test verifying user email"""
        # Create user without Google ID (unverified)
        user_data = UserCreate(
            email="unverified@example.com",
            name="Unverified User",
        )
        created_user = user_service.create_user(user_data)
        assert created_user.is_verified is False

        verified_user = user_service.verify_user_email(created_user.id)
        assert verified_user.is_verified is True

    def test_delete_user(self, user_service, sample_user_data):
        """Test deleting user"""
        created_user = user_service.create_user(sample_user_data)

        # Verify user exists
        assert user_service.get_user_by_id(created_user.id) is not None

        # Delete user
        success = user_service.delete_user(created_user.id)
        assert success is True

        # Verify user is deleted
        assert user_service.get_user_by_id(created_user.id) is None

    def test_delete_nonexistent_user(self, user_service):
        """Test deleting non-existent user"""
        non_existent_id = uuid.uuid4()
        success = user_service.delete_user(non_existent_id)
        assert success is False

    def test_create_from_google_oauth_new_user(self, user_service, sample_google_data):
        """Test creating new user from Google OAuth"""
        user, is_new = user_service.create_or_update_from_google_oauth(
            sample_google_data
        )

        assert is_new is True
        assert user.email == sample_google_data.email
        assert user.name == sample_google_data.name
        assert user.google_id == sample_google_data.google_id
        assert user.is_verified is True
        assert user.last_sign_in_at is not None

    def test_create_from_google_oauth_existing_user(
        self, user_service, sample_google_data
    ):
        """Test updating existing user from Google OAuth"""
        # Create user first
        user_service.create_or_update_from_google_oauth(sample_google_data)

        # Update with new Google data
        updated_google_data = GoogleOAuthData(
            google_id=sample_google_data.google_id,
            email=sample_google_data.email,
            name="Updated Name",
            avatar_url="https://example.com/new-avatar.jpg",
            email_verified=True,
        )

        user, is_new = user_service.create_or_update_from_google_oauth(
            updated_google_data
        )

        assert is_new is False
        assert user.name == "Updated Name"
        assert user.avatar_url == "https://example.com/new-avatar.jpg"

    def test_get_user_public(self, user_service, sample_user_data):
        """Test getting public user data"""
        created_user = user_service.create_user(sample_user_data)
        public_user = user_service.get_user_public(created_user.id)

        assert isinstance(public_user, UserPublic)
        assert public_user.id == str(created_user.id)
        assert public_user.email == created_user.email
        assert public_user.name == created_user.name
        # Should not include sensitive fields like google_id, is_active, etc.

    def test_get_users_pagination(self, user_service):
        """Test getting users with pagination"""
        # Create multiple users
        for i in range(5):
            user_data = UserCreate(
                email=f"user{i}@example.com",
                name=f"User {i}",
            )
            user_service.create_user(user_data)

        # Test pagination
        users_page1 = user_service.get_users(skip=0, limit=3)
        users_page2 = user_service.get_users(skip=3, limit=3)

        assert len(users_page1) == 3
        assert len(users_page2) == 2

    def test_get_users_search(self, user_service):
        """Test searching users"""
        # Create test users
        user_service.create_user(UserCreate(email="john@example.com", name="John Doe"))
        user_service.create_user(
            UserCreate(email="jane@example.com", name="Jane Smith")
        )
        user_service.create_user(
            UserCreate(email="bob@example.com", name="Bob Johnson")
        )

        # Search by name
        john_users = user_service.get_users(search="John")
        assert len(john_users) == 2  # John Doe and Bob Johnson

        # Search by email
        jane_users = user_service.get_users(search="jane@")
        assert len(jane_users) == 1
        assert jane_users[0].name == "Jane Smith"

    def test_count_users(self, user_service):
        """Test counting users"""
        assert user_service.count_users() == 0

        # Create users
        for i in range(3):
            user_data = UserCreate(email=f"user{i}@example.com", name=f"User {i}")
            user_service.create_user(user_data)

        assert user_service.count_users() == 3

        # Deactivate one user
        users = user_service.get_users()
        user_service.deactivate_user(users[0].id)

        assert user_service.count_users(active_only=True) == 2
        assert user_service.count_users(active_only=False) == 3

    def test_health_check(self, user_service):
        """Test user service health check"""
        health = user_service.health_check()

        assert health["status"] == "healthy"
        assert "user_count" in health
        assert health["user_count"] == 0
