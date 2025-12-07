"""
Security Utilities
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This module provides:
- Rate limiting for exports and API calls
- Stubs for SSO/Identity Provider integration
- Role-based access control helpers

Extension Points:
- SSO Integration: Add actual SSO logic in authenticate_user()
- RBAC: Extend permission checks for fine-grained access control
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
import logging

from analytics_hub_platform.infrastructure.settings import get_settings
from analytics_hub_platform.domain.models import User, UserRole


logger = logging.getLogger(__name__)


# ============================================
# RATE LIMITING
# ============================================

class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, limit: int, window_seconds: int, retry_after: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self.retry_after = retry_after
        super().__init__(
            f"Rate limit exceeded: {limit} requests per {window_seconds} seconds. "
            f"Retry after {retry_after} seconds."
        )


class RateLimiter:
    """
    Token bucket rate limiter.
    
    Tracks request counts per key within a sliding window.
    Designed to be simple for local PoC; production should use Redis.
    """
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed per window
            window_seconds: Window size in seconds
        """
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._requests: Dict[str, List[datetime]] = {}
    
    def _cleanup_old_requests(self, key: str) -> None:
        """Remove requests older than the window."""
        if key not in self._requests:
            return
        
        cutoff = datetime.now() - timedelta(seconds=self._window_seconds)
        self._requests[key] = [
            ts for ts in self._requests[key]
            if ts > cutoff
        ]
    
    def check(self, key: str) -> bool:
        """
        Check if request is allowed (does not consume quota).
        
        Args:
            key: Rate limit key (e.g., user_id, IP address)
            
        Returns:
            True if request would be allowed
        """
        self._cleanup_old_requests(key)
        current_count = len(self._requests.get(key, []))
        return current_count < self._max_requests
    
    def acquire(self, key: str) -> bool:
        """
        Try to acquire a request slot.
        
        Args:
            key: Rate limit key
            
        Returns:
            True if acquired, False if rate limited
        """
        self._cleanup_old_requests(key)
        
        if key not in self._requests:
            self._requests[key] = []
        
        if len(self._requests[key]) >= self._max_requests:
            return False
        
        self._requests[key].append(datetime.now())
        return True
    
    def acquire_or_raise(self, key: str) -> None:
        """
        Acquire a request slot or raise exception.
        
        Args:
            key: Rate limit key
            
        Raises:
            RateLimitExceeded: If rate limit exceeded
        """
        if not self.acquire(key):
            # Calculate retry after
            oldest = min(self._requests.get(key, [datetime.now()]))
            retry_after = int(
                (oldest + timedelta(seconds=self._window_seconds) - datetime.now()).total_seconds()
            )
            retry_after = max(1, retry_after)
            
            logger.warning(f"Rate limit exceeded for key: {key}")
            raise RateLimitExceeded(
                limit=self._max_requests,
                window_seconds=self._window_seconds,
                retry_after=retry_after,
            )
    
    def get_remaining(self, key: str) -> int:
        """
        Get remaining requests for a key.
        
        Args:
            key: Rate limit key
            
        Returns:
            Number of remaining requests in current window
        """
        self._cleanup_old_requests(key)
        current_count = len(self._requests.get(key, []))
        return max(0, self._max_requests - current_count)


# Global rate limiters
_export_limiter: Optional[RateLimiter] = None
_api_limiter: Optional[RateLimiter] = None


def get_rate_limiter(limiter_type: str = "export") -> RateLimiter:
    """
    Get a rate limiter instance.
    
    Args:
        limiter_type: "export" or "api"
        
    Returns:
        RateLimiter instance
    """
    global _export_limiter, _api_limiter
    
    settings = get_settings()
    
    if limiter_type == "export":
        if _export_limiter is None:
            _export_limiter = RateLimiter(
                max_requests=settings.rate_limit_exports,
                window_seconds=60,
            )
        return _export_limiter
    else:
        if _api_limiter is None:
            _api_limiter = RateLimiter(
                max_requests=settings.rate_limit_api,
                window_seconds=60,
            )
        return _api_limiter


def rate_limited(limiter_type: str = "api", key_func=None):
    """
    Decorator for rate-limited functions.
    
    Args:
        limiter_type: "export" or "api"
        key_func: Optional function to extract rate limit key from args
        
    Example:
        @rate_limited(limiter_type="export", key_func=lambda user_id, **kw: user_id)
        def export_pdf(user_id: str, ...):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            limiter = get_rate_limiter(limiter_type)
            
            # Determine rate limit key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = "global"
            
            limiter.acquire_or_raise(key)
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# ============================================
# SSO INTEGRATION STUBS
# ============================================

class SSOProvider(str, Enum):
    """Supported SSO providers (for future implementation)."""
    AZURE_AD = "azure_ad"
    OKTA = "okta"
    KEYCLOAK = "keycloak"


def authenticate_user(
    token: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> Optional[User]:
    """
    Authenticate a user.
    
    Extension Point: Implement actual SSO authentication here.
    
    For PoC, this returns a mock user based on the provided username.
    In production, this would:
    1. Validate JWT token from SSO provider
    2. Extract user claims (email, roles, groups)
    3. Map SSO groups to platform roles
    4. Create or update user in local database
    5. Return User model
    
    Args:
        token: JWT or OAuth token from SSO provider
        username: Username for basic auth (PoC only)
        password: Password for basic auth (PoC only)
        
    Returns:
        User model if authenticated, None otherwise
    """
    settings = get_settings()
    
    # In production: Validate token with SSO provider
    # Example for Azure AD:
    # if settings.sso_enabled and settings.sso_provider == "azure_ad":
    #     claims = validate_azure_ad_token(token, settings.sso_tenant_id, settings.sso_client_id)
    #     user = map_claims_to_user(claims)
    #     return user
    
    # PoC: Return mock user based on username
    mock_users = {
        "minister": User(
            id="user-001",
            tenant_id=settings.default_tenant_id,
            email="minister@mep.gov.sa",
            name="His Excellency the Minister",
            role=UserRole.MINISTER,
        ),
        "director": User(
            id="user-002",
            tenant_id=settings.default_tenant_id,
            email="director@mep.gov.sa",
            name="Director of Analytics",
            role=UserRole.DIRECTOR,
        ),
        "analyst": User(
            id="user-003",
            tenant_id=settings.default_tenant_id,
            email="analyst@mep.gov.sa",
            name="Senior Data Analyst",
            role=UserRole.ANALYST,
        ),
        "admin": User(
            id="user-004",
            tenant_id=settings.default_tenant_id,
            email="admin@mep.gov.sa",
            name="System Administrator",
            role=UserRole.ADMIN,
        ),
    }
    
    if username and username.lower() in mock_users:
        return mock_users[username.lower()]
    
    # Default to viewer
    return User(
        id="user-default",
        tenant_id=settings.default_tenant_id,
        email="viewer@mep.gov.sa",
        name="Default Viewer",
        role=UserRole.VIEWER,
    )


def get_user_from_token(token: str) -> Optional[User]:
    """
    Extract user from JWT token.
    
    Extension Point: Implement JWT validation here.
    
    Args:
        token: JWT token string
        
    Returns:
        User model if token valid, None otherwise
    """
    # In production:
    # 1. Decode and verify JWT signature
    # 2. Check expiration
    # 3. Extract claims
    # 4. Return User model
    
    # PoC: Always return None (not implemented)
    logger.debug("JWT token validation not implemented in PoC")
    return None


# ============================================
# ROLE-BASED ACCESS CONTROL
# ============================================

# Permission definitions
PERMISSIONS = {
    "view_executive_dashboard": [UserRole.MINISTER, UserRole.EXECUTIVE, UserRole.DIRECTOR, UserRole.ANALYST, UserRole.VIEWER],
    "view_director_dashboard": [UserRole.MINISTER, UserRole.EXECUTIVE, UserRole.DIRECTOR, UserRole.ANALYST],
    "view_analyst_dashboard": [UserRole.DIRECTOR, UserRole.ANALYST, UserRole.ADMIN],
    "view_admin_console": [UserRole.ADMIN],
    "export_pdf": [UserRole.MINISTER, UserRole.EXECUTIVE, UserRole.DIRECTOR, UserRole.ANALYST, UserRole.ADMIN],
    "export_ppt": [UserRole.MINISTER, UserRole.EXECUTIVE, UserRole.DIRECTOR, UserRole.ANALYST, UserRole.ADMIN],
    "export_excel": [UserRole.DIRECTOR, UserRole.ANALYST, UserRole.ADMIN],
    "edit_kpi_config": [UserRole.ADMIN],
    "manage_users": [UserRole.ADMIN],
    "manage_tenants": [UserRole.ADMIN],
    "view_raw_data": [UserRole.ANALYST, UserRole.ADMIN],
    "view_data_quality": [UserRole.DIRECTOR, UserRole.ANALYST, UserRole.ADMIN],
}


def has_permission(user: User, permission: str) -> bool:
    """
    Check if user has a specific permission.
    
    Args:
        user: User model
        permission: Permission name
        
    Returns:
        True if user has permission
    """
    if not user.is_active:
        return False
    
    allowed_roles = PERMISSIONS.get(permission, [])
    return user.role in allowed_roles


def require_permission(permission: str):
    """
    Decorator to require a permission for a function.
    
    Args:
        permission: Required permission name
        
    Example:
        @require_permission("export_pdf")
        def generate_report(user: User, ...):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract user from kwargs
            user = kwargs.get("user")
            if user is None:
                raise PermissionError("User not provided")
            
            if not has_permission(user, permission):
                raise PermissionError(
                    f"User {user.email} does not have permission: {permission}"
                )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def get_allowed_views(user: User) -> List[str]:
    """
    Get list of views the user can access.
    
    Args:
        user: User model
        
    Returns:
        List of view names
    """
    views = []
    
    if has_permission(user, "view_executive_dashboard"):
        views.append("executive")
    if has_permission(user, "view_director_dashboard"):
        views.append("director")
    if has_permission(user, "view_analyst_dashboard"):
        views.append("analyst")
    if has_permission(user, "view_admin_console"):
        views.append("admin")
    
    return views
