"""
File: app/schemas/auth.py
Purpose: Pydantic request/response schemas for authentication endpoints.
Responsibilities:
  - Validate register and login request bodies
  - Define the shape of user and token responses
Dependencies:
  - pydantic
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    """
    Description: Request body for POST /auth/register.
    Responsibilities:
      - Validate email format
      - Enforce minimum password length
    """

    name: str = Field(..., min_length=2, max_length=100, examples=["Shansit Goyal"])
    email: EmailStr = Field(..., examples=["shansit@example.com"])
    password: str = Field(..., min_length=8, examples=["SecurePass123!"])

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        """
        Purpose: Enforce basic password strength requirements.
        Parameters:
          value: The raw password string.
        Returns:
          str: Validated password.
        Raises:
          ValueError: If password does not meet requirements.
        """
        if not any(c.isupper() for c in value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one digit")
        return value


class LoginRequest(BaseModel):
    """
    Description: Request body for POST /auth/login.
    """

    email: EmailStr = Field(..., examples=["shansit@example.com"])
    password: str = Field(..., examples=["SecurePass123!"])


class UserResponse(BaseModel):
    """
    Description: Public user data returned in API responses (never includes password_hash).
    """

    id: uuid.UUID
    name: str
    email: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """
    Description: JWT token returned after successful register or login.
    """

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
