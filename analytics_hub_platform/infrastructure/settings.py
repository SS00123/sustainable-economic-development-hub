"""
Environment-Aware Settings
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This module provides environment-aware settings using Pydantic Settings.
Settings can be loaded from environment variables or .env files.
"""

import os
from typing import Optional
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    
    All settings can be overridden via environment variables.
    Example: DATABASE_URL=postgresql://... will override the default SQLite URL.
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
    sso_provider: Optional[str] = None
    sso_tenant_id: Optional[str] = None
    sso_client_id: Optional[str] = None
    sso_client_secret: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # Caching
    cache_enabled: bool = True
    cache_ttl_seconds: int = 300
    
    # Default tenant
    default_tenant_id: str = "mep-sa-001"
    default_tenant_name: str = "Ministry of Economy and Planning"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    
    # Streamlit
    streamlit_port: int = 8501
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"
    
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
