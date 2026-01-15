import os
from analytics_hub_platform.config.config import DatabaseConfig, SecurityConfig

def test_config_load_defaults():
    """Test that configuration loads with defaults."""
    db_config = DatabaseConfig.from_env()
    assert db_config.url == "sqlite:///analytics_hub.db"
    assert db_config.pool_size == 5

def test_config_load_env_override():
    """Test that environment variables override defaults."""
    os.environ["DATABASE_POOL_SIZE"] = "20"
    try:
        db_config = DatabaseConfig.from_env()
        assert db_config.pool_size == 20
    finally:
        del os.environ["DATABASE_POOL_SIZE"]

def test_security_config_defaults():
    """Test security config defaults."""
    sec_config = SecurityConfig()
    assert sec_config.rate_limit_api == 100
