"""
File: app/services/auth_service.py
Purpose: Business logic for user authentication operations.
Responsibilities:
  - Register new users (check uniqueness, hash password, insert to DB)
  - Authenticate users (verify email + password, return user object)
  - Keep auth logic isolated from API route handlers
Dependencies:
  - sqlalchemy.ext.asyncio (AsyncSession)
  - app.models.user (User)
  - app.core.security (hash_password, verify_password)
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.user import User
from app.core.security import hash_password, verify_password
from app.schemas.auth import RegisterRequest


class AuthService:
    """
    Description: Handles user registration and login business logic.
    Responsibilities:
      - Validate uniqueness of email on registration
      - Hash passwords before database storage
      - Verify credentials during login
    """

    def __init__(self, db: AsyncSession):
        """
        Purpose: Initialize service with a database session.
        Parameters:
          db: Async SQLAlchemy session injected by FastAPI dependency.
        """
        self.db = db

    async def register_user(self, payload: RegisterRequest) -> User:
        """
        Purpose: Create a new user account.
        Parameters:
          payload: Validated registration data (name, email, password).
        Returns:
          User: The newly created User ORM object.
        Raises:
          HTTPException 409: If a user with the given email already exists.
        """
        # Check for duplicate email
        existing = await self.db.execute(
            select(User).where(User.email == payload.email)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A user with email '{payload.email}' already exists",
            )

        user = User(
            name=payload.name,
            email=payload.email,
            password_hash=hash_password(payload.password),
        )
        self.db.add(user)
        await self.db.flush()   # Get the generated UUID without full commit
        await self.db.refresh(user)
        return user

    async def authenticate_user(self, email: str, password: str) -> User:
        """
        Purpose: Verify login credentials and return the authenticated user.
        Parameters:
          email: The email address provided during login.
          password: The plain-text password provided during login.
        Returns:
          User: The authenticated User ORM object.
        Raises:
          HTTPException 401: If email not found or password doesn't match.
        """
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if user is None or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated",
            )

        return user
