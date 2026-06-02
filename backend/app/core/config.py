"""
File: app/core/config.py
Purpose: Application configuration loaded from environment variables.
Responsibilities:
  - Define all configurable settings using Pydantic BaseSettings
  - Validate environment variable types at startup
  - Provide a single importable `settings` object used across the app
Dependencies:
  - pydantic-settings (reads from .env file automatically)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    Description: Centralized application settings read from environment variables.
    Responsibilities:
      - Parse and validate all .env values at application startup
      - Expose typed settings to all modules via the `settings` singleton
    """

    # ── Application ──────────────────────────────────────────────────────────
    app_name: str = "FounderOS"
    app_env: str = "development"
    debug: bool = True

    # ── Security ─────────────────────────────────────────────────────────────
    secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_days: int = 7

    # ── Database ─────────────────────────────────────────────────────────────
    database_url: str           # asyncpg URL for SQLAlchemy async engine
    sync_database_url: str      # psycopg2 URL for Alembic migrations

    # ── AI — Gemini (Primary) ────────────────────────────────────────────────
    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"

    # ── AI — OpenRouter (Fallback) ───────────────────────────────────────────
    openrouter_api_key: str
    openrouter_model: str = "mistralai/mistral-7b-instruct:free"

    # ── CORS ─────────────────────────────────────────────────────────────────
    frontend_url: str = "http://localhost:3000"

    # ── ChromaDB ─────────────────────────────────────────────────────────────
    chroma_persist_path: str = "./chroma_db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Purpose: Return a cached Settings instance (singleton pattern).
    Returns:
      Settings: The application settings object.
    Notes:
      - @lru_cache ensures .env is read only once per process
    """
    return Settings()


# Module-level singleton — import this everywhere
settings: Settings = get_settings()
