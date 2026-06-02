"""
File: app/core/security.py
Purpose: Authentication security utilities — password hashing and JWT management.
Responsibilities:
  - Hash passwords with bcrypt before storing in the database
  - Verify raw passwords against stored bcrypt hashes
  - Generate signed JWT access tokens
  - Decode and validate JWT tokens on each protected request
Dependencies:
  - passlib[bcrypt] for password hashing
  - python-jose[cryptography] for JWT operations
  - app.core.config (settings)
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# ── Password hashing ──────────────────────────────────────────────────────────
# bcrypt is the industry standard — slow enough to prevent brute-force attacks
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    Purpose: Hash a plain-text password using bcrypt.
    Parameters:
      plain_password: The user's raw password string.
    Returns:
      str: bcrypt hash suitable for database storage.
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Purpose: Verify a plain-text password against a stored bcrypt hash.
    Parameters:
      plain_password: The raw password provided during login.
      hashed_password: The bcrypt hash stored in the database.
    Returns:
      bool: True if password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT ───────────────────────────────────────────────────────────────────────

def create_access_token(user_id: str, email: str) -> str:
    """
    Purpose: Generate a signed JWT access token for an authenticated user.
    Parameters:
      user_id: The user's UUID (stored as 'sub' claim — standard JWT subject).
      email: The user's email address (stored as additional claim).
    Returns:
      str: Signed JWT string to be returned to the client.
    """
    expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt_expire_days)

    payload = {
        "sub": user_id,         # JWT standard — subject (user identifier)
        "email": email,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }

    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> Optional[dict]:
    """
    Purpose: Decode and validate a JWT access token.
    Parameters:
      token: The JWT string from the Authorization header.
    Returns:
      dict: Decoded payload containing 'sub' (user_id) and 'email'.
      None: If the token is invalid, expired, or malformed.
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError:
        return None
