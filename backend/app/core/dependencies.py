"""
File: app/core/dependencies.py
Purpose: FastAPI dependency injection helpers for authentication.
Responsibilities:
  - Extract and validate JWT from the Authorization header
  - Load the current authenticated user from the database
  - Raise HTTP 401 if token is missing, invalid, or user not found
Dependencies:
  - fastapi (Depends, HTTPBearer, HTTPException)
  - app.core.security (decode_access_token)
  - app.core.database (get_async_db)
  - app.models.user (User)
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_async_db
from app.core.security import decode_access_token
from app.models.user import User

# HTTPBearer scheme — expects: Authorization: Bearer <token>
bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_async_db),
) -> User:
    """
    Purpose: FastAPI dependency that authenticates the current request.
    Parameters:
      credentials: Extracted Bearer token from the Authorization header.
      db: Injected async database session.
    Returns:
      User: The authenticated user ORM object.
    Raises:
      HTTPException 401: If token is invalid, expired, or user not found.
    Usage:
      async def my_route(current_user: User = Depends(get_current_user)): ...
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode and validate JWT
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if not user_id:
        raise credentials_exception

    # Load user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise credentials_exception

    return user
