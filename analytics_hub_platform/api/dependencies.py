"""
API Dependencies
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

FastAPI dependency injection for database, auth, and services.
"""

import logging
from collections.abc import Generator

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from analytics_hub_platform.domain.models import User, UserRole
from analytics_hub_platform.infrastructure.auth import (
    get_jwt_handler,
    get_mock_users,
)
from analytics_hub_platform.infrastructure.exceptions import (
    InvalidTokenError,
    TokenExpiredError,
)
from analytics_hub_platform.infrastructure.repository import Repository, get_repository
from analytics_hub_platform.infrastructure.security import RBACManager
from analytics_hub_platform.infrastructure.settings import Settings, get_settings

logger = logging.getLogger(__name__)

# Security scheme for Swagger docs
security_scheme = HTTPBearer(auto_error=False)

# Type alias for backward compatibility
IndicatorRepository = Repository


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
    x_tenant_id: str | None = Header(None, alias="X-Tenant-ID"),
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


# User authentication with proper JWT validation
async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    authorization: str | None = Header(None),
    x_user_id: str | None = Header(None, alias="X-User-ID"),
    settings: Settings = Depends(get_settings),
) -> User:
    """
    Get current authenticated user from JWT token.

    In production, validates JWT token from Authorization header.
    In development mode, falls back to mock users for testing.

    Args:
        credentials: Bearer token from HTTPBearer scheme
        authorization: Raw Authorization header
        x_user_id: User ID header (for testing/development)

    Returns:
        Authenticated User model

    Raises:
        HTTPException: 401 if authentication fails
    """
    # Extract token from credentials or header
    token = None
    if credentials and credentials.credentials:
        token = credentials.credentials
    elif authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]

    # Try token-based authentication first
    if token:
        try:
            jwt_handler = get_jwt_handler()
            user = jwt_handler.get_user_from_token(token)
            logger.debug(f"Authenticated user via JWT: {user.email}")
            return user
        except TokenExpiredError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=e.message,
                headers={"WWW-Authenticate": "Bearer"},
            )

    # Development mode: allow header-based user switching for testing
    if settings.is_development():
        if x_user_id:
            mock_users = get_mock_users()
            user = mock_users.get(x_user_id.lower())
            if user:
                logger.debug(f"Development mode: Using mock user {x_user_id}")
                return user

        # Default demo user in development
        logger.debug("Development mode: Using default demo user")
        return get_mock_users()["demo"]

    # Production mode: require valid token
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )


# Optional authentication (for endpoints that work with/without auth)
async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    authorization: str | None = Header(None),
    settings: Settings = Depends(get_settings),
) -> User | None:
    """
    Get current user if authenticated, None otherwise.

    Use this for endpoints that have different behavior for
    authenticated vs anonymous users.
    """
    token = None
    if credentials and credentials.credentials:
        token = credentials.credentials
    elif authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]

    if token:
        try:
            jwt_handler = get_jwt_handler()
            return jwt_handler.get_user_from_token(token)
        except (InvalidTokenError, TokenExpiredError):
            return None

    # Development mode: return demo user
    if settings.is_development():
        return get_mock_users()["demo"]

    return None


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
        user: User = Depends(get_current_user),
    ) -> User:
        """
        Check if user has required role.

        Args:
            user: Current authenticated user

        Returns:
            User if authorized

        Raises:
            HTTPException: 403 if not authorized
        """
        if user.role not in self.allowed_roles:
            logger.warning(
                f"Access denied for user {user.email}: "
                f"role {user.role.value} not in {[r.value for r in self.allowed_roles]}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for this resource",
            )

        return user


# Convenience role dependencies
require_admin = RoleChecker([UserRole.ADMIN])
require_director = RoleChecker(
    [UserRole.ADMIN, UserRole.DIRECTOR, UserRole.EXECUTIVE, UserRole.MINISTER]
)
require_analyst = RoleChecker(
    [UserRole.ADMIN, UserRole.DIRECTOR, UserRole.EXECUTIVE, UserRole.MINISTER, UserRole.ANALYST]
)


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


# Rate limiting dependency with proper thread safety
class RateLimiter:
    """Thread-safe rate limiting dependency."""

    def __init__(self, requests_per_minute: int = 60):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests per minute
        """
        import threading

        self.requests_per_minute = requests_per_minute
        self._requests: dict = {}
        self._lock = threading.Lock()

    async def __call__(
        self,
        user: User = Depends(get_current_user),
    ) -> None:
        """
        Check rate limit for user.

        Args:
            user: Current authenticated user

        Raises:
            HTTPException: 429 if rate limit exceeded
        """
        import time

        user_id = user.id
        current_time = time.time()

        with self._lock:
            # Clean old entries
            if user_id in self._requests:
                self._requests[user_id] = [
                    t for t in self._requests[user_id] if current_time - t < 60
                ]
            else:
                self._requests[user_id] = []

            # Check limit
            if len(self._requests[user_id]) >= self.requests_per_minute:
                oldest = min(self._requests[user_id])
                retry_after = int(60 - (current_time - oldest))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again later.",
                    headers={"Retry-After": str(max(1, retry_after))},
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
        year: int | None = None,
        quarter: int | None = None,
        region: str | None = None,
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
    year: int | None = None,
    quarter: int | None = None,
    region: str | None = None,
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
