"""Infrastructure layer.

New stable import target for runtime infrastructure concerns.
This module re-exports commonly used infrastructure components for convenience.
The canonical implementation remains in `analytics_hub_platform.infrastructure`.
"""

from .database import get_engine, get_session

# Re-export commonly used infrastructure components
from analytics_hub_platform.infrastructure.settings import Settings, get_settings
from analytics_hub_platform.infrastructure.repository import Repository, get_repository
from analytics_hub_platform.infrastructure.db_init import initialize_database
from analytics_hub_platform.infrastructure.logging_config import get_logger, setup_logging
from analytics_hub_platform.infrastructure.caching import CacheManager, get_cache

__all__ = [
    # Database
    "get_engine",
    "get_session",
    "initialize_database",
    # Settings
    "Settings",
    "get_settings",
    # Repository
    "Repository",
    "get_repository",
    # Logging
    "get_logger",
    "setup_logging",
    # Caching
    "CacheManager",
    "get_cache",
]
