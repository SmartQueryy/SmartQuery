import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.user import (
    GoogleOAuthData,
    UserCreate,
    UserInDB,
    UserPublic,
    UserTable,
    UserUpdate,
)
from services.database_service import db_service


class UserService:
    """Service for user database operations"""

    def __init__(self):
        self.db_service = db_service

    def create_user(self, user_data: UserCreate) -> UserInDB:
        """Create a new user in the database"""
        with self.db_service.get_session() as session:
            try:
                # Check if user already exists
                existing_user = self.get_user_by_email(user_data.email)
                if existing_user:
                    raise ValueError(
                        f"User with email {user_data.email} already exists"
                    )

                # Create new user
                db_user = UserTable(
                    email=user_data.email,
                    name=user_data.name,
                    avatar_url=user_data.avatar_url,
                    google_id=user_data.google_id,
                    is_verified=True if user_data.google_id else False,
                )

                session.add(db_user)
                session.commit()
                session.refresh(db_user)

                return UserInDB.model_validate(db_user)

            except IntegrityError as e:
                session.rollback()
                if "users_email_key" in str(e):
                    raise ValueError(
                        f"User with email {user_data.email} already exists"
                    )
                elif "users_google_id_key" in str(e):
                    raise ValueError(f"User with Google ID already exists")
                else:
                    raise ValueError(f"Database error: {str(e)}")

    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[UserInDB]:
        """Get user by ID"""
        with self.db_service.get_session() as session:
            user = session.query(UserTable).filter(UserTable.id == user_id).first()
            return UserInDB.model_validate(user) if user else None

    def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email address"""
        with self.db_service.get_session() as session:
            user = session.query(UserTable).filter(UserTable.email == email).first()
            return UserInDB.model_validate(user) if user else None

    def get_user_by_google_id(self, google_id: str) -> Optional[UserInDB]:
        """Get user by Google OAuth ID"""
        with self.db_service.get_session() as session:
            user = (
                session.query(UserTable)
                .filter(UserTable.google_id == google_id)
                .first()
            )
            return UserInDB.model_validate(user) if user else None

    def update_user(self, user_id: uuid.UUID, user_update: UserUpdate) -> UserInDB:
        """Update user information"""
        with self.db_service.get_session() as session:
            user = session.query(UserTable).filter(UserTable.id == user_id).first()

            if not user:
                raise ValueError(f"User with ID {user_id} not found")

            # Update only provided fields
            update_data = user_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(user, field, value)

            try:
                session.commit()
                session.refresh(user)
                return UserInDB.model_validate(user)

            except IntegrityError as e:
                session.rollback()
                raise ValueError(f"Update failed: {str(e)}")

    def update_last_sign_in(self, user_id: uuid.UUID) -> UserInDB:
        """Update user's last sign-in timestamp"""
        return self.update_user(user_id, UserUpdate(last_sign_in_at=datetime.utcnow()))

    def deactivate_user(self, user_id: uuid.UUID) -> UserInDB:
        """Deactivate a user account"""
        return self.update_user(user_id, UserUpdate(is_active=False))

    def activate_user(self, user_id: uuid.UUID) -> UserInDB:
        """Activate a user account"""
        return self.update_user(user_id, UserUpdate(is_active=True))

    def verify_user_email(self, user_id: uuid.UUID) -> UserInDB:
        """Mark user email as verified"""
        return self.update_user(user_id, UserUpdate(is_verified=True))

    def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True,
        search: Optional[str] = None,
    ) -> List[UserInDB]:
        """Get list of users with optional filtering"""
        with self.db_service.get_session() as session:
            query = session.query(UserTable)

            # Filter by active status
            if active_only:
                query = query.filter(UserTable.is_active == True)

            # Search filter
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        UserTable.name.ilike(search_term),
                        UserTable.email.ilike(search_term),
                    )
                )

            # Pagination
            users = query.offset(skip).limit(limit).all()
            return [UserInDB.model_validate(user) for user in users]

    def count_users(self, active_only: bool = True) -> int:
        """Count total number of users"""
        with self.db_service.get_session() as session:
            query = session.query(UserTable)
            if active_only:
                query = query.filter(UserTable.is_active == True)
            return query.count()

    def delete_user(self, user_id: uuid.UUID) -> bool:
        """Delete a user (hard delete)"""
        with self.db_service.get_session() as session:
            user = session.query(UserTable).filter(UserTable.id == user_id).first()

            if not user:
                return False

            session.delete(user)
            session.commit()
            return True

    def create_or_update_from_google_oauth(
        self, google_data: GoogleOAuthData
    ) -> tuple[UserInDB, bool]:
        """Create or update user from Google OAuth data

        Returns:
            tuple: (UserInDB, is_new_user)
        """
        # Try to find existing user by Google ID first
        existing_user = self.get_user_by_google_id(google_data.google_id)

        if existing_user:
            # Update existing user with latest Google data
            updated_user = self.update_user(
                existing_user.id,
                UserUpdate(
                    name=google_data.name,
                    avatar_url=google_data.avatar_url,
                    is_verified=google_data.email_verified,
                    last_sign_in_at=datetime.utcnow(),
                ),
            )
            return updated_user, False

        # Try to find by email (in case user exists but no Google ID)
        existing_user = self.get_user_by_email(google_data.email)

        if existing_user:
            # Link Google account to existing user
            updated_user = self.update_user(
                existing_user.id,
                UserUpdate(
                    google_id=google_data.google_id,
                    name=google_data.name,
                    avatar_url=google_data.avatar_url,
                    is_verified=google_data.email_verified,
                    last_sign_in_at=datetime.utcnow(),
                ),
            )
            return updated_user, False

        # Create new user from Google data
        new_user_data = UserCreate(
            email=google_data.email,
            name=google_data.name,
            avatar_url=google_data.avatar_url,
            google_id=google_data.google_id,
        )

        new_user = self.create_user(new_user_data)
        # Update sign-in time
        updated_user = self.update_last_sign_in(new_user.id)
        return updated_user, True

    def get_user_public(self, user_id: uuid.UUID) -> Optional[UserPublic]:
        """Get public user data for API responses"""
        user = self.get_user_by_id(user_id)
        return UserPublic.from_db_user(user) if user else None

    def health_check(self) -> dict:
        """Check if user service and database connection is healthy"""
        try:
            with self.db_service.get_session() as session:
                # Try to count users
                user_count = session.query(UserTable).count()
                return {
                    "status": "healthy",
                    "message": f"User service operational. Total users: {user_count}",
                    "user_count": user_count,
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"User service error: {str(e)}",
                "user_count": 0,
            }


# Global instance
user_service = UserService()
