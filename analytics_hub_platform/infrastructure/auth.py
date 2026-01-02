"""
JWT Authentication Module
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Provides JWT token creation, validation, and user authentication.
"""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from analytics_hub_platform.domain.models import User, UserRole
from analytics_hub_platform.infrastructure.exceptions import (
    AuthenticationError,
    InvalidTokenError,
    TokenExpiredError,
)
from analytics_hub_platform.infrastructure.settings import get_settings

logger = logging.getLogger(__name__)


# Try to import jose for JWT handling
try:
    from jose import ExpiredSignatureError, JWTError, jwt

    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    logger.warning("python-jose not installed. JWT authentication will use fallback mode.")


class JWTHandler:
    """
    Handles JWT token creation and validation.

    In production with SSO, tokens would be validated against the identity provider.
    For standalone mode, this handles local JWT creation and validation.
    """

    def __init__(self):
        self._settings = get_settings()

    @property
    def _secret_key(self) -> str:
        """Get the secret key, handling SecretStr and None."""
        if self._settings.jwt_secret_key is None:
            raise AuthenticationError(
                message="JWT secret key not configured",
                code="JWT_NOT_CONFIGURED",
            )
        return self._settings.jwt_secret_key.get_secret_value()

    @property
    def _algorithm(self) -> str:
        return self._settings.jwt_algorithm

    @property
    def _expire_minutes(self) -> int:
        return self._settings.jwt_access_token_expire_minutes

    def create_access_token(
        self,
        user: User,
        expires_delta: timedelta | None = None,
    ) -> str:
        """
        Create a JWT access token for a user.

        Args:
            user: User model
            expires_delta: Optional custom expiration time

        Returns:
            JWT token string

        Raises:
            AuthenticationError: If JWT creation fails
        """
        if not JWT_AVAILABLE:
            # Fallback: return a simple encoded token for PoC
            return f"poc_token:{user.id}:{user.role.value}"

        try:
            expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=self._expire_minutes))

            payload = {
                "sub": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role.value,
                "tenant_id": user.tenant_id,
                "exp": expire,
                "iat": datetime.now(UTC),
                "iss": "analytics-hub",
            }

            token = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
            return token

        except Exception as e:
            logger.error(f"Failed to create JWT token: {e}")
            raise AuthenticationError(
                message="Failed to create access token",
                code="TOKEN_CREATION_FAILED",
            )

    def verify_token(self, token: str) -> dict[str, Any]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded token payload

        Raises:
            InvalidTokenError: If token is invalid
            TokenExpiredError: If token has expired
        """
        if not JWT_AVAILABLE:
            # Fallback: parse simple PoC token
            return self._parse_poc_token(token)

        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
                options={"verify_exp": True},
            )
            return payload

        except ExpiredSignatureError:
            raise TokenExpiredError()
        except JWTError as e:
            logger.warning(f"JWT validation failed: {e}")
            raise InvalidTokenError(
                message="Invalid token",
                details={"error": str(e)},
            )

    def _parse_poc_token(self, token: str) -> dict[str, Any]:
        """Parse a simple PoC token (fallback when jose not available)."""
        if not token.startswith("poc_token:"):
            raise InvalidTokenError(message="Invalid token format")

        try:
            parts = token.split(":")
            if len(parts) != 3:
                raise InvalidTokenError(message="Invalid token structure")

            return {
                "sub": parts[1],
                "role": parts[2],
            }
        except Exception:
            raise InvalidTokenError(message="Failed to parse token")

    def get_user_from_token(self, token: str) -> User:
        """
        Extract User model from a validated JWT token.

        Args:
            token: JWT token string

        Returns:
            User model

        Raises:
            InvalidTokenError: If token is invalid
            TokenExpiredError: If token has expired
        """
        payload = self.verify_token(token)

        try:
            role_value = payload.get("role", "viewer")
            role = (
                UserRole(role_value)
                if role_value in [r.value for r in UserRole]
                else UserRole.VIEWER
            )

            return User(
                id=payload.get("sub", "unknown"),
                tenant_id=payload.get("tenant_id", self._settings.default_tenant_id),
                email=payload.get("email", ""),
                name=payload.get("name", "Unknown User"),
                role=role,
                is_active=True,
            )
        except Exception as e:
            logger.error(f"Failed to extract user from token: {e}")
            raise InvalidTokenError(
                message="Invalid token payload",
                details={"error": str(e)},
            )


# Mock users for development/demo mode
def get_mock_users() -> dict[str, User]:
    """Get mock users for development mode."""
    settings = get_settings()

    return {
        "minister": User(
            id="user-001",
            tenant_id=settings.default_tenant_id,
            email="minister@mep.gov.sa",
            name="His Excellency the Minister",
            role=UserRole.MINISTER,
            is_active=True,
        ),
        "executive": User(
            id="user-002",
            tenant_id=settings.default_tenant_id,
            email="executive@mep.gov.sa",
            name="Deputy Minister",
            role=UserRole.EXECUTIVE,
            is_active=True,
        ),
        "director": User(
            id="user-003",
            tenant_id=settings.default_tenant_id,
            email="director@mep.gov.sa",
            name="Director of Analytics",
            role=UserRole.DIRECTOR,
            is_active=True,
        ),
        "analyst": User(
            id="user-004",
            tenant_id=settings.default_tenant_id,
            email="analyst@mep.gov.sa",
            name="Senior Data Analyst",
            role=UserRole.ANALYST,
            is_active=True,
        ),
        "admin": User(
            id="user-005",
            tenant_id=settings.default_tenant_id,
            email="admin@mep.gov.sa",
            name="System Administrator",
            role=UserRole.ADMIN,
            is_active=True,
        ),
        "demo": User(
            id="user-demo",
            tenant_id=settings.default_tenant_id,
            email="demo@ministry.gov.sa",
            name="Demo User",
            role=UserRole.ANALYST,
            is_active=True,
        ),
    }


def authenticate_user(
    username: str | None = None,
    password: str | None = None,
    token: str | None = None,
) -> User | None:
    """
    Authenticate a user by username/password or token.

    In production, this would integrate with SSO/Identity Provider.
    For development, uses mock users.

    Args:
        username: Username for basic auth
        password: Password for basic auth (not validated in dev mode)
        token: JWT token for token-based auth

    Returns:
        User if authenticated, None otherwise
    """
    settings = get_settings()

    # Token-based authentication
    if token:
        try:
            jwt_handler = JWTHandler()
            return jwt_handler.get_user_from_token(token)
        except (InvalidTokenError, TokenExpiredError):
            return None

    # Username-based authentication (development mode)
    if username and settings.is_development():
        mock_users = get_mock_users()
        user = mock_users.get(username.lower())
        if user:
            return user

    # Default: return demo user in development
    if settings.is_development():
        return get_mock_users().get("demo")

    return None


# Global JWT handler instance
_jwt_handler: JWTHandler | None = None


def get_jwt_handler() -> JWTHandler:
    """Get the global JWT handler instance."""
    global _jwt_handler
    if _jwt_handler is None:
        _jwt_handler = JWTHandler()
    return _jwt_handler


__all__ = [
    "JWTHandler",
    "get_jwt_handler",
    "authenticate_user",
    "get_mock_users",
    "JWT_AVAILABLE",
]
