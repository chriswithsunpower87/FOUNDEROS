"""
File: alembic/env.py
Purpose: Alembic migration environment configuration.
Responsibilities:
  - Load the sync database URL from application settings
  - Import all SQLAlchemy models so Alembic can detect schema changes
  - Configure online (live DB) migration mode
Dependencies:
  - alembic
  - app.core.config (settings)
  - All app.models modules (must be imported for autogenerate to work)
"""

import sys
import os

# Add backend/ directory to Python path so app imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.models.base import Base

# Import all models — required for autogenerate to detect them
from app.models import user, idea, report, agent_run  # noqa: F401

# Alembic Config object
config = context.config

# Set the database URL from our settings (overrides alembic.ini placeholder)
config.set_main_option("sqlalchemy.url", settings.sync_database_url)

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# The metadata object Alembic inspects to auto-generate migrations
target_metadata = Base.metadata


def run_migrations_online() -> None:
    """
    Purpose: Run migrations against a live database connection.
    Notes:
      - This is the standard mode used for all environments
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,          # Detect column type changes
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
