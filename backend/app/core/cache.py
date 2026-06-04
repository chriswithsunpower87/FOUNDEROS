"""
File: app/core/cache.py
Purpose: Optional Redis cache layer for agent report outputs.
Responsibilities:
  - Connect to Redis on startup (fails gracefully if Redis is unavailable)
  - Cache completed agent report outputs with a 24-hour TTL
  - Invalidate cached reports when an idea is re-analyzed
  - Provide a cache-aside pattern: check Redis first, fall back to Postgres
Dependencies:
  - redis[asyncio] (optional — app works without it)
  - app.core.config (settings)

Design Decision:
  Redis is optional. If REDIS_URL is not set or Redis is unreachable,
  all cache operations become no-ops and the app falls back to Postgres.
  This means zero configuration required in development.

Key Schema:
  founderos:reports:{idea_id}:{version}  → JSON list of all reports
  TTL: 86400 seconds (24 hours)
"""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

# ── Optional Redis client — None if Redis is not configured ──────────────────
_redis_client = None


async def init_cache() -> None:
    """
    Purpose: Attempt to connect to Redis. Called on app startup.
      Silently skips if REDIS_URL is not set or Redis is unreachable.
      The app continues working without cache — just slower on repeated reads.
    """
    global _redis_client

    try:
        from app.core.config import settings
        if not settings.redis_url:
            logger.info("ℹ️  REDIS_URL not set — caching disabled")
            return

        import redis.asyncio as aioredis
        client = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=2,   # Fail fast if Redis is down
        )
        # Ping to verify connection
        await client.ping()
        _redis_client = client
        logger.info("✅ Redis cache connected")

    except Exception as exc:
        logger.warning(f"⚠️  Redis unavailable (caching disabled): {exc}")
        _redis_client = None


async def close_cache() -> None:
    """
    Purpose: Gracefully close the Redis connection on app shutdown.
    """
    global _redis_client
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None


# ── Cache TTL ─────────────────────────────────────────────────────────────────
CACHE_TTL_SECONDS = 86_400  # 24 hours


def _reports_key(idea_id: str, version: int) -> str:
    """
    Purpose: Build the Redis key for a set of reports.
    Parameters:
      idea_id: UUID of the idea as a string.
      version: Analysis version number.
    Returns:
      str: Namespaced Redis key.
    """
    return f"founderos:reports:{idea_id}:{version}"


async def cache_reports(idea_id: str, version: int, reports: list[dict[str, Any]]) -> None:
    """
    Purpose: Store a serialized list of report dicts in Redis.
      Called after all agents complete for a given version.
    Parameters:
      idea_id: UUID string of the idea.
      version: Analysis version number.
      reports: List of report dicts (already serialized from ORM objects).
    """
    if not _redis_client:
        return
    try:
        key = _reports_key(idea_id, version)
        await _redis_client.setex(key, CACHE_TTL_SECONDS, json.dumps(reports))
        logger.debug(f"📦 Cached reports for {idea_id} v{version}")
    except Exception as exc:
        logger.warning(f"⚠️  Cache write failed (non-fatal): {exc}")


async def get_cached_reports(idea_id: str, version: int) -> list[dict[str, Any]] | None:
    """
    Purpose: Retrieve cached reports from Redis.
    Parameters:
      idea_id: UUID string of the idea.
      version: Analysis version number.
    Returns:
      list[dict]: Cached report dicts if present, None on cache miss.
    """
    if not _redis_client:
        return None
    try:
        key = _reports_key(idea_id, version)
        raw = await _redis_client.get(key)
        if raw:
            logger.debug(f"⚡ Cache HIT for {idea_id} v{version}")
            return json.loads(raw)
        logger.debug(f"💨 Cache MISS for {idea_id} v{version}")
        return None
    except Exception as exc:
        logger.warning(f"⚠️  Cache read failed (non-fatal): {exc}")
        return None


async def invalidate_reports(idea_id: str) -> None:
    """
    Purpose: Delete all cached report versions for an idea.
      Called when the user triggers a re-analysis so the old cache
      is evicted and fresh data is fetched from Postgres.
    Parameters:
      idea_id: UUID string of the idea.
    """
    if not _redis_client:
        return
    try:
        # Use SCAN to find all version keys for this idea
        pattern = f"founderos:reports:{idea_id}:*"
        keys = []
        async for key in _redis_client.scan_iter(pattern):
            keys.append(key)
        if keys:
            await _redis_client.delete(*keys)
            logger.debug(f"🗑️  Invalidated {len(keys)} cache entries for {idea_id}")
    except Exception as exc:
        logger.warning(f"⚠️  Cache invalidation failed (non-fatal): {exc}")
