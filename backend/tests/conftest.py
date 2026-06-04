"""
File: tests/conftest.py
Purpose: Pytest fixtures shared across all test modules.
Responsibilities:
  - Create an in-memory SQLite test database (no external Postgres needed)
  - Provide an async test client with the DB override injected
  - Provide helper fixtures: test user, auth token, sample idea
Dependencies:
  - pytest-asyncio
  - httpx (AsyncClient)
  - sqlalchemy (async SQLite for testing)
"""

import asyncio
import uuid
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import get_async_db
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.base import Base
from app.models.idea import Idea, IdeaStatus
from app.models.user import User

# ── In-memory SQLite for tests (no Postgres required) ─────────────────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables():
    """
    Purpose: Create all ORM tables in the test SQLite DB once per session.
    This runs before any test in the session.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Purpose: Yield a test database session that rolls back after each test.
    This ensures tests are fully isolated from each other.
    """
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Purpose: Provide an httpx AsyncClient wired to the FastAPI test app.
      Overrides the get_async_db dependency to use the test session.
    """
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_async_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """
    Purpose: Create and persist a test user in the test database.
    Returns: User ORM object ready to use in tests.
    """
    user = User(
        id=uuid.uuid4(),
        name="Test User",
        email="test@founderos.com",
        hashed_password=hash_password("TestPassword123!"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
def auth_token(test_user: User) -> str:
    """
    Purpose: Generate a valid JWT for the test user.
    Returns: Signed JWT string ready to use in Authorization headers.
    """
    return create_access_token(user_id=str(test_user.id), email=test_user.email)


@pytest_asyncio.fixture
def auth_headers(auth_token: str) -> dict:
    """
    Purpose: Build Authorization headers dict for authenticated API calls.
    Returns: dict with Authorization: Bearer <token>.
    """
    return {"Authorization": f"Bearer {auth_token}"}


@pytest_asyncio.fixture
async def sample_idea(db_session: AsyncSession, test_user: User) -> Idea:
    """
    Purpose: Create a DRAFT idea owned by the test user.
    Returns: Idea ORM object ready to use in tests.
    """
    idea = Idea(
        id=uuid.uuid4(),
        user_id=test_user.id,
        title="AI Fitness App",
        problem_statement="People can't stay consistent with their workouts",
        target_audience="Busy professionals aged 25-40",
        status=IdeaStatus.DRAFT,
        is_public=False,
    )
    db_session.add(idea)
    await db_session.commit()
    await db_session.refresh(idea)
    return idea
