"""
Environment-Aware Settings
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This module provides environment-aware settings using Pydantic Settings.
Settings can be loaded from environment variables, .env files, or Streamlit secrets.
"""

import logging
from functools import lru_cache

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""

    pass


def _get_streamlit_secrets():
    """Try to load Streamlit secrets if available."""
    try:
        import streamlit as st

        if hasattr(st, "secrets"):
            # Check if secrets actually exist before accessing
            try:
                # This will raise an error if no secrets.toml exists
                if len(st.secrets) > 0:
                    return st.secrets
            except Exception:
                # Secrets file doesn't exist or is empty
                pass
    except (ImportError, AttributeError):
        pass
    return None


class Settings(BaseSettings):
    """
    Application settings with environment variable support.

    All settings can be overridden via:
    1. Streamlit secrets (.streamlit/secrets.toml)
    2. Environment variables
    3. .env file
    4. Default values

    Priority: Streamlit secrets > Environment > .env > Defaults
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Sustainable Economic Development Analytics Hub"
    app_version: str = "1.0.0"
    environment: str = "development"  # development, staging, production
    debug: bool = True

    # Database
    database_url: str = "sqlite:///analytics_hub.db"
    database_echo: bool = False

    # Security
    rate_limit_exports: int = 10
    rate_limit_api: int = 100
    session_timeout_minutes: int = 60

    # SSO Integration (stubs for future)
    # Extension Point: Add SSO configuration when integrating with identity provider
    sso_enabled: bool = False
    sso_provider: str | None = None
    sso_tenant_id: str | None = None
    sso_client_id: str | None = None
    sso_client_secret: str | None = None

    # Logging
    log_level: str = "INFO"
    log_file: str | None = None

    # Caching
    cache_enabled: bool = True
    cache_ttl_seconds: int = 300

    # ML defaults
    ml_random_state: int = 42
    anomaly_if_contamination: float = 0.1
    synthetic_seed: int = 42

    # JWT Configuration
    # SECURITY: In production, JWT_SECRET_KEY MUST be set via environment variable
    # The default value is only for development/testing
    jwt_secret_key: SecretStr | None = (
        None  # REQUIRED in production - set via JWT_SECRET_KEY env var
    )
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    # Flag to allow insecure defaults (only for testing)
    allow_insecure_jwt_secret: bool = False

    # LLM Configuration
    llm_provider: str = "auto"  # "openai", "anthropic", "mock", or "auto"
    llm_model_name: str | None = None  # Model name (provider-specific)
    llm_api_key: SecretStr | None = None  # API key (prefer env variables)
    openai_api_key: SecretStr | None = None  # OpenAI API key (SecretStr prevents logging)
    anthropic_api_key: SecretStr | None = None  # Anthropic API key (SecretStr prevents logging)
    llm_timeout: int = 30  # API timeout in seconds
    llm_max_retries: int = 2  # Maximum retry attempts
    llm_cache_ttl: int = 3600  # Cache TTL in seconds (1 hour)

    # Default tenant
    default_tenant_id: str = "mep-sa-001"
    default_tenant_name: str = "Ministry of Economy and Planning"

    # API
    api_host: str = "0.0.0.0"  # nosec B104 - Intentional for container deployment
    api_port: int = 8000
    api_prefix: str = "/api/v1"

    # Streamlit
    streamlit_port: int = 8501

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """
        Validate that required settings are provided in production.

        SECURITY: Ensures JWT secret is properly configured in production.
        In development, allows insecure defaults for convenience.
        """
        if self.is_production():
            # JWT secret is REQUIRED in production
            if self.jwt_secret_key is None:
                raise ConfigurationError(
                    "JWT_SECRET_KEY environment variable is REQUIRED in production. "
                    'Generate a secure key with: python -c "import secrets; print(secrets.token_urlsafe(32))"'
                )

            # Check for weak JWT secret in production
            secret_value = self.jwt_secret_key.get_secret_value()
            if len(secret_value) < 32:
                raise ConfigurationError(
                    "JWT_SECRET_KEY must be at least 32 characters in production."
                )

            if secret_value in ("change-this-secret-in-production-env", "test-secret", "secret"):
                raise ConfigurationError(
                    "JWT_SECRET_KEY appears to be a default/test value. "
                    "Use a secure random key in production."
                )
        else:
            # Development mode - use insecure default if not provided
            if self.jwt_secret_key is None:
                if self.allow_insecure_jwt_secret or self.environment in (
                    "development",
                    "test",
                    "testing",
                ):
                    # Use development-only default (will be rejected in production)
                    object.__setattr__(
                        self,
                        "jwt_secret_key",
                        SecretStr("dev-only-insecure-secret-do-not-use-in-production"),
                    )
                    # Silent in dev - this is expected behavior
                    logger.debug(
                        "Using development JWT secret. "
                        "JWT_SECRET_KEY will be required in production."
                    )
                else:
                    raise ConfigurationError(
                        "JWT_SECRET_KEY not set. Set the environment variable or "
                        "use ALLOW_INSECURE_JWT_SECRET=true for development."
                    )

        return self

    def __init__(self, **kwargs):
        """Initialize settings with Streamlit secrets support."""
        # Try to load from Streamlit secrets first
        secrets = _get_streamlit_secrets()
        if secrets:
            # Override with Streamlit secrets if available
            if "database" in secrets:
                kwargs.setdefault(
                    "database_url",
                    secrets["database"].get("DATABASE_URL", kwargs.get("database_url")),
                )
                kwargs.setdefault(
                    "default_tenant_id",
                    secrets["database"].get("DEFAULT_TENANT_ID", kwargs.get("default_tenant_id")),
                )

            if "app" in secrets:
                kwargs.setdefault(
                    "environment", secrets["app"].get("ENVIRONMENT", kwargs.get("environment"))
                )
                kwargs.setdefault("debug", secrets["app"].get("DEBUG", kwargs.get("debug")))
                kwargs.setdefault(
                    "log_level", secrets["app"].get("LOG_LEVEL", kwargs.get("log_level"))
                )

        super().__init__(**kwargs)

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development or test environment."""
        return self.environment.lower() in ("development", "test", "testing")

    def is_test(self) -> bool:
        """Check if running in test environment."""
        return self.environment.lower() in ("test", "testing")

    @property
    def db_path(self) -> str | None:
        """
        Extract database file path from SQLite URL.

        Returns the path portion of a SQLite database URL,
        or None if using a different database type.
        """
        if self.database_url.startswith("sqlite:///"):
            return self.database_url.replace("sqlite:///", "")
        return None

    def get_database_url(self) -> str:
        """
        Get the database URL, potentially modified for the environment.

        Extension Point: Add database URL transformation for different
        environments (e.g., adding SSL parameters for production).
        """
        return self.database_url


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Get the global settings instance.

    Uses LRU cache for singleton behavior.
    Call get_settings.cache_clear() to reload settings.
    """
    return Settings()
