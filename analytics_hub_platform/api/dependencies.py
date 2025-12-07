"""
API Dependencies
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

FastAPI dependency injection for database, auth, and services.
"""

from typing import Optional, Generator
from functools import lru_cache

from fastapi import Depends, HTTPException, Header, status

from analytics_hub_platform.infrastructure.settings import Settings, get_settings
from analytics_hub_platform.infrastructure.repository import IndicatorRepository, get_repository
from analytics_hub_platform.infrastructure.security import RBACManager, UserRole


# Database session dependency
def get_db_session() -> Generator:
    """
    Get database session.
    
    In production, this would be a proper SQLAlchemy session.
    For the PoC, we use the repository pattern.
    
    Yields:
        Database session
    """
    # For PoC, we use the singleton repository
    yield get_repository()


# Tenant extraction
async def get_current_tenant(
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
    settings: Settings = Depends(get_settings),
) -> str:
    """
    Extract current tenant from request headers.
    
    Args:
        x_tenant_id: Tenant ID from header
        settings: Application settings
    
    Returns:
        Tenant ID string
    """
    if x_tenant_id:
        return x_tenant_id
    
    # Fall back to default tenant
    return settings.default_tenant_id


# User authentication (stub for SSO integration)
async def get_current_user(
    authorization: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
) -> dict:
    """
    Get current authenticated user.
    
    In production, this would validate JWT/SSO tokens.
    For the PoC, we use a stub implementation.
    
    Args:
        authorization: Authorization header
        x_user_id: User ID header (for testing)
    
    Returns:
        User information dictionary
    """
    # Stub implementation for demo
    return {
        "user_id": x_user_id or "demo_user",
        "name": "Demo User",
        "email": "demo@ministry.gov.sa",
        "role": UserRole.ANALYST,
    }


# Role-based access control
class RoleChecker:
    """Dependency for checking user roles."""
    
    def __init__(self, allowed_roles: list):
        """
        Initialize with allowed roles.
        
        Args:
            allowed_roles: List of allowed UserRole values
        """
        self.allowed_roles = allowed_roles
        self.rbac = RBACManager()
    
    async def __call__(
        self,
        user: dict = Depends(get_current_user),
    ) -> dict:
        """
        Check if user has required role.
        
        Args:
            user: Current user info
        
        Returns:
            User info if authorized
        
        Raises:
            HTTPException: If not authorized
        """
        user_role = user.get("role", UserRole.ANALYST)
        
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        
        return user


# Convenience role dependencies
require_admin = RoleChecker([UserRole.ADMIN])
require_director = RoleChecker([UserRole.ADMIN, UserRole.DIRECTOR, UserRole.EXECUTIVE, UserRole.MINISTER])
require_analyst = RoleChecker([UserRole.ADMIN, UserRole.DIRECTOR, UserRole.EXECUTIVE, UserRole.MINISTER, UserRole.ANALYST])


# Repository dependency
async def get_indicator_repository(
    settings: Settings = Depends(get_settings),
) -> IndicatorRepository:
    """
    Get indicator repository instance.
    
    Args:
        settings: Application settings
    
    Returns:
        IndicatorRepository instance
    """
    return get_repository()


# Rate limiting dependency
class RateLimiter:
    """Simple rate limiting dependency."""
    
    def __init__(self, requests_per_minute: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per minute
        """
        self.requests_per_minute = requests_per_minute
        self._requests: dict = {}
    
    async def __call__(
        self,
        user: dict = Depends(get_current_user),
    ) -> None:
        """
        Check rate limit for user.
        
        Args:
            user: Current user info
        
        Raises:
            HTTPException: If rate limit exceeded
        """
        import time
        
        user_id = user.get("user_id", "anonymous")
        current_time = time.time()
        
        # Clean old entries
        if user_id in self._requests:
            self._requests[user_id] = [
                t for t in self._requests[user_id]
                if current_time - t < 60
            ]
        else:
            self._requests[user_id] = []
        
        # Check limit
        if len(self._requests[user_id]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
            )
        
        # Record request
        self._requests[user_id].append(current_time)


# Pagination parameters
class PaginationParams:
    """Pagination parameters for list endpoints."""
    
    def __init__(
        self,
        page: int = 1,
        page_size: int = 25,
        max_page_size: int = 100,
    ):
        """
        Initialize pagination.
        
        Args:
            page: Page number (1-indexed)
            page_size: Items per page
            max_page_size: Maximum allowed page size
        """
        self.page = max(1, page)
        self.page_size = min(max(1, page_size), max_page_size)
        self.offset = (self.page - 1) * self.page_size
        self.limit = self.page_size


async def get_pagination(
    page: int = 1,
    page_size: int = 25,
) -> PaginationParams:
    """
    Get pagination parameters from query.
    
    Args:
        page: Page number
        page_size: Items per page
    
    Returns:
        PaginationParams instance
    """
    return PaginationParams(page=page, page_size=page_size)


# Filter parameters
class FilterDependency:
    """Common filter parameters for indicator endpoints."""
    
    def __init__(
        self,
        year: Optional[int] = None,
        quarter: Optional[int] = None,
        region: Optional[str] = None,
    ):
        """
        Initialize filters.
        
        Args:
            year: Filter by year
            quarter: Filter by quarter
            region: Filter by region
        """
        self.year = year
        self.quarter = quarter
        self.region = region
        
        # Validate
        if quarter is not None and quarter not in [1, 2, 3, 4]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quarter must be 1, 2, 3, or 4",
            )


async def get_filters(
    year: Optional[int] = None,
    quarter: Optional[int] = None,
    region: Optional[str] = None,
) -> FilterDependency:
    """
    Get filter parameters from query.
    
    Args:
        year: Filter by year
        quarter: Filter by quarter
        region: Filter by region
    
    Returns:
        FilterDependency instance
    """
    return FilterDependency(year=year, quarter=quarter, region=region)
