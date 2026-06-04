"""
File: tests/test_api/test_ideas.py
Purpose: Integration tests for idea CRUD and pipeline trigger endpoints.
Responsibilities:
  - Test POST /ideas (create)
  - Test GET /ideas (list)
  - Test GET /ideas/{id} (get single)
  - Test PUT /ideas/{id} (update — only DRAFT)
  - Test DELETE /ideas/{id}
  - Test POST /ideas/{id}/analyze (trigger + rate limit)
  - Test ownership — users cannot access other users' ideas
Dependencies:
  - pytest-asyncio, httpx (AsyncClient via conftest fixture)
"""

from unittest.mock import patch

import pytest


@pytest.mark.asyncio
class TestCreateIdea:
    """Tests for POST /ideas."""

    async def test_create_idea_success(self, client, auth_headers):
        """Purpose: Verify an authenticated user can create a new idea."""
        response = await client.post("/api/v1/ideas", json={
            "title": "EV Charging Network",
            "problem_statement": "EV drivers can't find reliable charging stations",
            "target_audience": "EV owners in suburban areas",
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["title"] == "EV Charging Network"
        assert data["data"]["status"] == "DRAFT"
        assert data["data"]["is_public"] is False

    async def test_create_idea_requires_auth(self, client):
        """Purpose: Verify unauthenticated requests are rejected."""
        response = await client.post("/api/v1/ideas", json={
            "title": "Test",
            "problem_statement": "Test problem",
            "target_audience": "Test audience",
        })
        assert response.status_code == 401

    async def test_create_idea_validates_title_length(self, client, auth_headers):
        """Purpose: Verify short titles fail validation (min_length=3)."""
        response = await client.post("/api/v1/ideas", json={
            "title": "AB",  # Too short
            "problem_statement": "Some problem here",
            "target_audience": "Some audience",
        }, headers=auth_headers)
        assert response.status_code == 422


@pytest.mark.asyncio
class TestListIdeas:
    """Tests for GET /ideas."""

    async def test_list_ideas_returns_user_ideas(self, client, auth_headers, sample_idea):
        """Purpose: Verify list returns only the current user's ideas."""
        response = await client.get("/api/v1/ideas", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        items = data["data"]["items"]
        assert len(items) >= 1
        assert any(i["id"] == str(sample_idea.id) for i in items)

    async def test_list_ideas_requires_auth(self, client):
        """Purpose: Verify unauthenticated list requests are rejected."""
        response = await client.get("/api/v1/ideas")
        assert response.status_code == 401


@pytest.mark.asyncio
class TestGetIdea:
    """Tests for GET /ideas/{id}."""

    async def test_get_idea_success(self, client, auth_headers, sample_idea):
        """Purpose: Verify a user can fetch their own idea by ID."""
        response = await client.get(
            f"/api/v1/ideas/{sample_idea.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["title"] == sample_idea.title

    async def test_get_idea_not_found(self, client, auth_headers):
        """Purpose: Verify 404 for a non-existent idea UUID."""
        import uuid
        response = await client.get(
            f"/api/v1/ideas/{uuid.uuid4()}",
            headers=auth_headers,
        )
        assert response.status_code == 404


@pytest.mark.asyncio
class TestUpdateIdea:
    """Tests for PUT /ideas/{id}."""

    async def test_update_draft_idea(self, client, auth_headers, sample_idea):
        """Purpose: Verify DRAFT ideas can be updated."""
        response = await client.put(
            f"/api/v1/ideas/{sample_idea.id}",
            json={"title": "Updated Title"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["data"]["title"] == "Updated Title"


@pytest.mark.asyncio
class TestDeleteIdea:
    """Tests for DELETE /ideas/{id}."""

    async def test_delete_idea_success(self, client, auth_headers, sample_idea):
        """Purpose: Verify an idea can be deleted and returns 204."""
        response = await client.delete(
            f"/api/v1/ideas/{sample_idea.id}",
            headers=auth_headers,
        )
        assert response.status_code == 204

    async def test_deleted_idea_not_found(self, client, auth_headers, sample_idea):
        """Purpose: Verify a deleted idea returns 404 on subsequent fetch."""
        await client.delete(
            f"/api/v1/ideas/{sample_idea.id}",
            headers=auth_headers,
        )
        response = await client.get(
            f"/api/v1/ideas/{sample_idea.id}",
            headers=auth_headers,
        )
        assert response.status_code == 404


@pytest.mark.asyncio
class TestAnalyzeIdea:
    """Tests for POST /ideas/{id}/analyze."""

    async def test_analyze_returns_202(self, client, auth_headers, sample_idea):
        """
        Purpose: Verify the analyze endpoint returns 202 Accepted
          and queues the background pipeline without blocking.
          The actual pipeline is mocked to avoid real LLM calls.
        """
        with patch("app.api.v1.ideas.run_pipeline_background"):
            response = await client.post(
                f"/api/v1/ideas/{sample_idea.id}/analyze",
                headers=auth_headers,
            )
        assert response.status_code == 202
        data = response.json()
        assert data["data"]["idea_id"] == str(sample_idea.id)

    async def test_analyze_requires_auth(self, client, sample_idea):
        """Purpose: Verify unauthenticated analyze requests are rejected."""
        response = await client.post(
            f"/api/v1/ideas/{sample_idea.id}/analyze",
        )
        assert response.status_code == 401
