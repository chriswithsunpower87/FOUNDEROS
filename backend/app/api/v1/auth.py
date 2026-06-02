"""
File: app/api/v1/auth.py
Purpose: FastAPI route handlers for authentication endpoints.
Responsibilities:
  - POST /auth/register — create new user account
  - POST /auth/login — authenticate and return JWT
  - GET /auth/me — return current user profile
Dependencies:
  - app.services.auth_service (AuthService)
  - app.core.security (create_access_token)
  - app.core.dependencies (get_current_user)
  - app.schemas.auth (RegisterRequest, LoginRequest, TokenResponse, UserResponse)
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.dependencies import get_current_user
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.schemas.common import APIResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_async_db),
) -> APIResponse[TokenResponse]:
    """
    Purpose: Create a new FounderOS user account and return a JWT.
    Parameters:
      payload: Registration data (name, email, password).
      db: Injected async database session.
    Returns:
      APIResponse containing the JWT and user profile.
    """
    service = AuthService(db)
    user = await service.register_user(payload)
    token = create_access_token(user_id=str(user.id), email=user.email)

    return APIResponse(
        data=TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(user),
        ),
        message="Account created successfully",
    )


@router.post(
    "/login",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Login with email and password",
)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_async_db),
) -> APIResponse[TokenResponse]:
    """
    Purpose: Authenticate user credentials and return a JWT.
    Parameters:
      payload: Login data (email, password).
      db: Injected async database session.
    Returns:
      APIResponse containing the JWT and user profile.
    """
    service = AuthService(db)
    user = await service.authenticate_user(payload.email, payload.password)
    token = create_access_token(user_id=str(user.id), email=user.email)

    return APIResponse(
        data=TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(user),
        ),
        message="Login successful",
    )


@router.get(
    "/me",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> APIResponse[UserResponse]:
    """
    Purpose: Return the authenticated user's profile.
    Parameters:
      current_user: Injected authenticated user (from JWT).
    Returns:
      APIResponse containing the user profile.
    """
    return APIResponse(data=UserResponse.model_validate(current_user))
