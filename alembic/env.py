"""
Alembic Environment Configuration
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This module configures Alembic for database migrations.
It integrates with the application's settings and models.
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import application settings and models
from analytics_hub_platform.infrastructure.settings import get_settings
from analytics_hub_platform.infrastructure.db_init import metadata

# Alembic Config object - access to .ini file values
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate support
target_metadata = metadata


def get_database_url() -> str:
    """
    Get database URL from settings or environment.
    
    Priority:
    1. ANALYTICS_HUB_DATABASE_URL environment variable
    2. Application settings
    3. alembic.ini default
    """
    # Check environment variable first (production pattern)
    env_url = os.environ.get("ANALYTICS_HUB_DATABASE_URL")
    if env_url:
        return env_url
    
    # Try application settings
    try:
        settings = get_settings()
        return settings.database_url
    except Exception:
        pass
    
    # Fall back to alembic.ini default
    return config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    
    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.
    
    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    
    In this scenario we need to create an Engine and associate
    a connection with the context.
    """
    # Override URL in configuration
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_database_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            # Include object names in autogenerate
            include_object=lambda obj, name, type_, reflected, compare_to: True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
