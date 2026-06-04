"""
File: app/core/limiter.py
Purpose: Configures the SlowAPI rate limiter for FastAPI.
Responsibilities:
  - Create a shared Limiter instance used across all route modules
  - Key requests by the authenticated user's JWT subject (sub) claim
    so limits are per-user, not per-IP
  - Fall back to client IP for unauthenticated endpoints
Dependencies:
  - slowapi (Limiter, _rate_limit_exceeded_handler)
  - fastapi (Request)
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

from app.core.security import decode_access_token


def _get_user_identifier(request: Request) -> str:
    """
    Purpose: Extract the user identifier for rate limit bucketing.
      Uses the JWT sub claim (user UUID) so limits are per-user.
      Falls back to client IP for unauthenticated requests.
    Parameters:
      request: The incoming FastAPI Request object.
    Returns:
      str: A stable identifier for this client (user ID or IP address).
    """
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            return f"user:{payload['sub']}"

    # Unauthenticated — fall back to IP
    return get_remote_address(request)


# Shared limiter instance — import this in route files
limiter = Limiter(
    key_func=_get_user_identifier,
    default_limits=[],          # No global limit — set per-endpoint
    headers_enabled=True,       # Add X-RateLimit-* headers to responses
)
