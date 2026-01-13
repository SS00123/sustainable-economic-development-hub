"""Data access layer.

This package is the forward-looking home for repository and DB-facing helpers.
Currently it wraps existing implementations in `analytics_hub_platform.infrastructure`
so imports can migrate safely.
"""

from .repository import AnalyticsRepository

__all__ = ["AnalyticsRepository"]
