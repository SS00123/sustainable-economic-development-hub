"""
Application Configuration
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This module contains the central configuration for the analytics platform.
Configuration values can be overridden via environment variables.
"""

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml


@dataclass
class DatabaseConfig:
    """Database configuration settings."""

    url: str = "sqlite:///analytics_hub.db"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Create configuration from environment variables."""
        return cls(
            url=os.getenv("DATABASE_URL", "sqlite:///analytics_hub.db"),
            echo=os.getenv("DATABASE_ECHO", "false").lower() == "true",
            pool_size=int(os.getenv("DATABASE_POOL_SIZE", "5")),
            max_overflow=int(os.getenv("DATABASE_MAX_OVERFLOW", "10")),
        )


@dataclass
class SecurityConfig:
    """Security configuration settings."""

    rate_limit_exports: int = 10  # Max exports per minute
    rate_limit_api: int = 100  # Max API calls per minute
    session_timeout_minutes: int = 60

    # SSO Integration (stubs for future implementation)
    sso_enabled: bool = False
    sso_provider: str | None = None  # e.g., "azure_ad", "okta"
    sso_tenant_id: str | None = None
    sso_client_id: str | None = None

    @classmethod
    def from_env(cls) -> "SecurityConfig":
        """Create configuration from environment variables."""
        return cls(
            rate_limit_exports=int(os.getenv("RATE_LIMIT_EXPORTS", "10")),
            rate_limit_api=int(os.getenv("RATE_LIMIT_API", "100")),
            session_timeout_minutes=int(os.getenv("SESSION_TIMEOUT_MINUTES", "60")),
            sso_enabled=os.getenv("SSO_ENABLED", "false").lower() == "true",
            sso_provider=os.getenv("SSO_PROVIDER"),
            sso_tenant_id=os.getenv("SSO_TENANT_ID"),
            sso_client_id=os.getenv("SSO_CLIENT_ID"),
        )


@dataclass
class LoggingConfig:
    """Logging configuration settings."""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str | None = None

    @classmethod
    def from_env(cls) -> "LoggingConfig":
        """Create configuration from environment variables."""
        return cls(
            level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE"),
        )


@dataclass
class ModuleConfig:
    """Module enablement configuration."""

    # Core modules that can be enabled/disabled
    sustainability_enabled: bool = True
    economic_development_enabled: bool = True
    labor_skills_enabled: bool = True
    data_quality_enabled: bool = True

    @classmethod
    def from_env(cls) -> "ModuleConfig":
        """Create configuration from environment variables."""
        return cls(
            sustainability_enabled=os.getenv("MODULE_SUSTAINABILITY", "true").lower() == "true",
            economic_development_enabled=os.getenv("MODULE_ECONOMIC", "true").lower() == "true",
            labor_skills_enabled=os.getenv("MODULE_LABOR", "true").lower() == "true",
            data_quality_enabled=os.getenv("MODULE_DATA_QUALITY", "true").lower() == "true",
        )

    def get_enabled_modules(self) -> list[str]:
        """Return list of enabled module names."""
        modules = []
        if self.sustainability_enabled:
            modules.append("sustainability")
        if self.economic_development_enabled:
            modules.append("economic_development")
        if self.labor_skills_enabled:
            modules.append("labor_skills")
        if self.data_quality_enabled:
            modules.append("data_quality")
        return modules


@dataclass
class AppConfig:
    """
    Main application configuration.

    This configuration class centralizes all settings for the Analytics Hub platform.
    Values can be set via environment variables or programmatically.

    Extension Point: Add new configuration sections here for additional platform features.
    """

    # Application metadata
    app_name: str = "Sustainable Economic Development Analytics Hub"
    app_version: str = "1.0.0"
    environment: str = "development"

    # Default tenant (Ministry of Economy and Planning)
    default_tenant_id: str = "mep-sa-001"
    default_tenant_name: str = "Ministry of Economy and Planning"

    # Paths
    base_path: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    kpi_catalog_path: Path = field(
        default_factory=lambda: Path(__file__).parent / "kpi_catalog.yaml"
    )
    exports_path: Path = field(default_factory=lambda: Path(__file__).parent.parent / "exports")

    # Sub-configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    modules: ModuleConfig = field(default_factory=ModuleConfig)

    # Feature flags
    enable_exports: bool = True
    enable_api: bool = True
    enable_caching: bool = True
    cache_ttl_seconds: int = 300  # 5 minutes

    # Default filter values
    default_year: int = 2024
    default_quarter: int = 4
    default_region: str = "all"
    default_language: str = "en"

    # Available regions (Saudi Arabia administrative regions)
    regions: list[str] = field(
        default_factory=lambda: [
            "Riyadh",
            "Makkah",
            "Madinah",
            "Eastern Province",
            "Qassim",
            "Asir",
            "Tabuk",
            "Hail",
            "Northern Borders",
            "Jazan",
            "Najran",
            "Al Bahah",
            "Al Jawf",
        ]
    )

    # Available years for data
    available_years: list[int] = field(default_factory=lambda: [2020, 2021, 2022, 2023, 2024])

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create configuration from environment variables."""
        return cls(
            app_name=os.getenv("APP_NAME", "Sustainable Economic Development Analytics Hub"),
            app_version=os.getenv("APP_VERSION", "1.0.0"),
            environment=os.getenv("ENVIRONMENT", "development"),
            default_tenant_id=os.getenv("DEFAULT_TENANT_ID", "mep-sa-001"),
            default_tenant_name=os.getenv(
                "DEFAULT_TENANT_NAME", "Ministry of Economy and Planning"
            ),
            database=DatabaseConfig.from_env(),
            security=SecurityConfig.from_env(),
            logging=LoggingConfig.from_env(),
            modules=ModuleConfig.from_env(),
            enable_exports=os.getenv("ENABLE_EXPORTS", "true").lower() == "true",
            enable_api=os.getenv("ENABLE_API", "true").lower() == "true",
            enable_caching=os.getenv("ENABLE_CACHING", "true").lower() == "true",
            cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "300")),
        )

    def load_kpi_catalog(self) -> dict:
        """Load KPI catalog from YAML file."""
        if self.kpi_catalog_path.exists():
            with open(self.kpi_catalog_path, encoding="utf-8") as f:
                return yaml.safe_load(f)
        return {"kpis": []}

    def ensure_exports_path(self) -> Path:
        """Ensure exports directory exists and return path."""
        self.exports_path.mkdir(parents=True, exist_ok=True)
        return self.exports_path


# Global configuration instance (singleton pattern)
_config_instance: AppConfig | None = None


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    """
    Get the global application configuration.

    Uses LRU cache to ensure single instance.
    Call get_config.cache_clear() to reload configuration.
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = AppConfig.from_env()
    return _config_instance


def reload_config() -> AppConfig:
    """Reload configuration from environment."""
    global _config_instance
    get_config.cache_clear()
    _config_instance = None
    return get_config()


# Import from centralized constants for backwards compatibility
from analytics_hub_platform.config.constants import SAUDI_REGIONS as REGIONS

__all__ = ["get_config", "reload_config", "AppConfig", "REGIONS"]
