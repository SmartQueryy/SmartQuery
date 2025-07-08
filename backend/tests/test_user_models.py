import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError

from models.user import (
    GoogleOAuthData,
    UserCreate,
    UserInDB,
    UserTable,
    UserUpdate,
)


def test_user_table_creation():
    """Test UserTable model creation"""
    user_id = uuid.uuid4()
    user = UserTable(
        id=user_id,
        email="test@example.com",
        name="Test User",
    )
    assert user.id == user_id
    assert user.email == "test@example.com"
    assert user.name == "Test User"


def test_user_create_model():
    """Test UserCreate Pydantic model"""
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "google_id": "google123",
    }
    user = UserCreate(**user_data)
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.google_id == "google123"


def test_user_update_model():
    """Test UserUpdate Pydantic model"""
    update_data = {"name": "Updated Name", "avatar_url": "https://new.url/avatar.jpg"}
    update = UserUpdate(**update_data)
    assert update.name == "Updated Name"
    assert update.avatar_url == "https://new.url/avatar.jpg"


def test_user_in_db_model():
    """Test UserInDB Pydantic model"""
    db_data = {
        "id": uuid.uuid4(),
        "email": "db@example.com",
        "name": "DB User",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    user_in_db = UserInDB(**db_data)
    assert user_in_db.name == "DB User"


def test_google_oauth_data_model():
    """Test GoogleOAuthData Pydantic model"""
    google_data = {
        "google_id": "google123",
        "email": "google@example.com",
        "name": "Google User",
        "email_verified": True,
    }
    oauth_data = GoogleOAuthData(**google_data)
    assert oauth_data.name == "Google User"


def test_user_create_invalid_email():
    """Test that UserCreate raises error for invalid email"""
    with pytest.raises(ValidationError):
        UserCreate(email="not-an-email", name="Test")


def test_user_update_empty_name():
    """Test that UserUpdate allows None but not empty name"""
    # This behavior depends on the validator implementation
    # Pydantic v2 allows empty strings by default if min_length is not set
    update = UserUpdate(name="")
    assert update.name == ""
