"""
API Package
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

FastAPI-based REST API for data access.
"""

from analytics_hub_platform.api.dependencies import get_current_tenant, get_db_session
from analytics_hub_platform.api.routers import create_api_router

__all__ = [
    "create_api_router",
    "get_db_session",
    "get_current_tenant",
]
