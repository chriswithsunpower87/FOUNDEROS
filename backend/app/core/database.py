"""
File: app/core/database.py
Purpose: SQLAlchemy async database engine and session factory.
Responsibilities:
  - Create the async SQLAlchemy engine connected to Supabase PostgreSQL
  - Provide an async session factory for dependency injection in API routes
  - Provide a sync session factory for use in background tasks (agents)
Dependencies:
  - sqlalchemy[asyncio], asyncpg
  - app.core.config (settings)
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# ── Async engine — used by API route handlers ─────────────────────────────────
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,       # Logs SQL in development
    pool_pre_ping=True,        # Verify connection before each use
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,    # Keep objects usable after commit
    autocommit=False,
    autoflush=False,
)

# ── Sync engine — used by Alembic migrations and background agent tasks ───────
sync_engine = create_engine(
    settings.sync_database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_async_db() -> AsyncSession:
    """
    Purpose: FastAPI dependency that yields an async database session.
    Yields:
      AsyncSession: Active database session, automatically closed after request.
    Usage:
      async def my_route(db: AsyncSession = Depends(get_async_db)): ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db() -> Session:
    """
    Purpose: Create a synchronous database session for background tasks.
    Returns:
      Session: Active sync database session. Caller must close it.
    Usage:
      Used inside agent pipeline (background thread, not async context).
    """
    return SyncSessionLocal()
