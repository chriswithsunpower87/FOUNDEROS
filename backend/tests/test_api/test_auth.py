"""
File: tests/test_api/test_auth.py
Purpose: Integration tests for authentication endpoints.
Responsibilities:
  - Test POST /api/v1/auth/register (success + duplicate email)
  - Test POST /api/v1/auth/login (success + wrong password)
  - Test GET /api/v1/auth/me (authenticated + unauthenticated)
Dependencies:
  - pytest-asyncio, httpx (AsyncClient via conftest fixture)
"""

import pytest


@pytest.mark.asyncio
class TestRegister:
    """Integration tests for the user registration endpoint."""

    async def test_register_success(self, client):
        """Purpose: Verify a new user can register and receives a JWT."""
        response = await client.post("/api/v1/auth/register", json={
            "name": "Alice Founder",
            "email": "alice@test.com",
            "password": "SecurePass123!",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["access_token"] is not None
        assert data["data"]["user"]["email"] == "alice@test.com"

    async def test_register_duplicate_email(self, client, test_user):
        """Purpose: Verify 400 is returned when registering with an existing email."""
        response = await client.post("/api/v1/auth/register", json={
            "name": "Duplicate",
            "email": test_user.email,  # Already exists
            "password": "SecurePass123!",
        })
        assert response.status_code in (400, 409)

    async def test_register_invalid_email(self, client):
        """Purpose: Verify 422 is returned for invalid email format."""
        response = await client.post("/api/v1/auth/register", json={
            "name": "Test",
            "email": "not-an-email",
            "password": "SecurePass123!",
        })
        assert response.status_code == 422


@pytest.mark.asyncio
class TestLogin:
    """Integration tests for the login endpoint."""

    async def test_login_success(self, client, test_user):
        """Purpose: Verify login returns a JWT for valid credentials."""
        response = await client.post("/api/v1/auth/login", json={
            "email": test_user.email,
            "password": "TestPassword123!",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data["data"]

    async def test_login_wrong_password(self, client, test_user):
        """Purpose: Verify 401 is returned for incorrect password."""
        response = await client.post("/api/v1/auth/login", json={
            "email": test_user.email,
            "password": "WrongPassword!",
        })
        assert response.status_code == 401

    async def test_login_unknown_email(self, client):
        """Purpose: Verify 401 is returned for unregistered email."""
        response = await client.post("/api/v1/auth/login", json={
            "email": "nobody@test.com",
            "password": "AnyPassword123!",
        })
        assert response.status_code == 401


@pytest.mark.asyncio
class TestGetMe:
    """Integration tests for the /auth/me profile endpoint."""

    async def test_get_me_authenticated(self, client, auth_headers, test_user):
        """Purpose: Verify /auth/me returns the current user's profile."""
        response = await client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["email"] == test_user.email

    async def test_get_me_unauthenticated(self, client):
        """Purpose: Verify /auth/me returns 401 without a token."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    async def test_get_me_invalid_token(self, client):
        """Purpose: Verify /auth/me returns 401 for a tampered token."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer not.a.valid.token"},
        )
        assert response.status_code == 401
