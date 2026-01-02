"""
Async Database Tests
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Tests for async database operations.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from analytics_hub_platform.infrastructure.async_db import (
    AsyncDatabaseManager,
    AsyncRepository,
    get_async_database_url,
    get_async_db,
)


class TestAsyncDatabaseUrl:
    """Tests for database URL conversion."""

    def test_sqlite_conversion(self):
        """Test SQLite URL conversion."""
        sync_url = "sqlite:///analytics.db"
        async_url = get_async_database_url(sync_url)

        assert async_url == "sqlite+aiosqlite:///analytics.db"

    def test_postgresql_conversion(self):
        """Test PostgreSQL URL conversion."""
        sync_url = "postgresql://user:pass@localhost/db"
        async_url = get_async_database_url(sync_url)

        assert async_url == "postgresql+asyncpg://user:pass@localhost/db"

    def test_postgres_shorthand_conversion(self):
        """Test postgres:// URL conversion."""
        sync_url = "postgres://user:pass@localhost/db"
        async_url = get_async_database_url(sync_url)

        assert async_url == "postgresql+asyncpg://user:pass@localhost/db"

    def test_already_async_url(self):
        """Test that async URLs are returned unchanged."""
        async_url = "postgresql+asyncpg://user:pass@localhost/db"
        result = get_async_database_url(async_url)

        assert result == async_url


class TestAsyncDatabaseManager:
    """Tests for async database manager."""

    def test_singleton_pattern(self):
        """Test that manager is a singleton."""
        manager1 = AsyncDatabaseManager()
        manager2 = AsyncDatabaseManager()

        assert manager1 is manager2

    def test_get_async_db_returns_manager(self):
        """Test global getter returns manager."""
        manager = get_async_db()

        assert manager is not None
        assert isinstance(manager, AsyncDatabaseManager)

    def test_engine_created_lazily(self):
        """Test that engine is created on first access."""
        manager = AsyncDatabaseManager()

        # Engine should be created when accessed
        engine = manager.engine
        assert engine is not None

    def test_session_factory_created_lazily(self):
        """Test that session factory is created on first access."""
        manager = AsyncDatabaseManager()

        factory = manager.session_factory
        assert factory is not None


class TestAsyncRepository:
    """Tests for async repository."""

    def test_repository_initialization(self):
        """Test repository initialization."""
        repo = AsyncRepository()

        assert repo is not None
        assert repo._db is not None

    def test_repository_with_custom_db(self):
        """Test repository with custom database manager."""
        db = get_async_db()
        repo = AsyncRepository(db=db)

        assert repo._db is db


@pytest.mark.asyncio
class TestAsyncRepositoryQueries:
    """Async tests for repository queries."""

    async def test_health_check(self):
        """Test database health check."""
        repo = AsyncRepository()

        # Mock the session to avoid actual DB connection
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock()

        with patch.object(repo._db, "session") as mock_ctx:
            mock_ctx.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_ctx.return_value.__aexit__ = AsyncMock()

            result = await repo.health_check()

            # Should return True when query succeeds
            assert result is True

    async def test_get_tenant_not_found(self):
        """Test getting non-existent tenant."""
        repo = AsyncRepository()

        # Mock empty result
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.mappings.return_value.first.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch.object(repo._db, "session") as mock_ctx:
            mock_ctx.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_ctx.return_value.__aexit__ = AsyncMock()

            result = await repo.get_tenant("nonexistent")

            assert result is None

    async def test_get_all_indicators_with_filters(self):
        """Test getting indicators with filters."""
        from analytics_hub_platform.domain.models import FilterParams

        repo = AsyncRepository()
        filters = FilterParams(tenant_id="test-tenant", year=2024, quarter=1, region="Riyadh")

        # Mock result
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.mappings.return_value.all.return_value = [
            {"year": 2024, "quarter": 1, "region": "Riyadh", "gdp_growth": 3.5}
        ]
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch.object(repo._db, "session") as mock_ctx:
            mock_ctx.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_ctx.return_value.__aexit__ = AsyncMock()

            result = await repo.get_all_indicators("test-tenant", filters)

            assert len(result) == 1
            assert result[0]["region"] == "Riyadh"

    async def test_get_timeseries_invalid_indicator(self):
        """Test getting timeseries with invalid indicator raises error."""
        repo = AsyncRepository()

        with pytest.raises(ValueError) as exc_info:
            await repo.get_timeseries(
                "test-tenant",
                "invalid_indicator_name",
            )

        assert "Unknown indicator" in str(exc_info.value)

    async def test_get_regional_comparison_invalid_indicator(self):
        """Test regional comparison with invalid indicator raises error."""
        repo = AsyncRepository()

        with pytest.raises(ValueError) as exc_info:
            await repo.get_regional_comparison(
                "test-tenant",
                2024,
                1,
                "invalid_indicator",
            )

        assert "Unknown indicator" in str(exc_info.value)


class TestAsyncDatabaseLifespan:
    """Tests for FastAPI lifespan integration."""

    def test_lifespan_import(self):
        """Test that lifespan context manager can be imported."""
        from analytics_hub_platform.infrastructure.async_db import database_lifespan

        assert database_lifespan is not None
        assert callable(database_lifespan)

    def test_get_async_repository_import(self):
        """Test that repository dependency can be imported."""
        from analytics_hub_platform.infrastructure.async_db import get_async_repository

        assert get_async_repository is not None
        assert asyncio.iscoroutinefunction(get_async_repository)
