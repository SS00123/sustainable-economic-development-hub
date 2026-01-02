"""
Async Database Module
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Async database support using SQLAlchemy 2.0 async engine.
Provides async repository for FastAPI endpoints.

For PostgreSQL production use, install: pip install asyncpg
For SQLite async (development), uses aiosqlite automatically.
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, Optional

from sqlalchemy import and_, select, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import AsyncAdaptedQueuePool, NullPool

from analytics_hub_platform.domain.models import (
    FilterParams,
)
from analytics_hub_platform.infrastructure.db_init import (
    sustainability_indicators,
    tenants,
    users,
)
from analytics_hub_platform.infrastructure.settings import get_settings

logger = logging.getLogger(__name__)


def get_async_database_url(sync_url: str) -> str:
    """
    Convert sync database URL to async version.

    - sqlite:///path -> sqlite+aiosqlite:///path
    - postgresql://... -> postgresql+asyncpg://...

    Args:
        sync_url: Synchronous database URL

    Returns:
        Async-compatible database URL
    """
    if sync_url.startswith("sqlite:///"):
        return sync_url.replace("sqlite:///", "sqlite+aiosqlite:///")
    elif sync_url.startswith("postgresql://"):
        return sync_url.replace("postgresql://", "postgresql+asyncpg://")
    elif sync_url.startswith("postgres://"):
        return sync_url.replace("postgres://", "postgresql+asyncpg://")
    else:
        # Return as-is, might already be async
        return sync_url


class AsyncDatabaseManager:
    """
    Manages async database connections and sessions.

    Provides connection pooling and session factory for async operations.
    Suitable for FastAPI dependency injection.
    """

    _instance: Optional["AsyncDatabaseManager"] = None

    def __new__(cls):
        """Singleton pattern for database manager."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize async database manager."""
        if self._initialized:
            return

        self._settings = get_settings()
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker | None = None
        self._initialized = True

    @property
    def engine(self) -> AsyncEngine:
        """Get or create async engine."""
        if self._engine is None:
            async_url = get_async_database_url(self._settings.database_url)

            # Configure pool based on database type
            engine_kwargs = {
                "echo": self._settings.database_echo,
            }

            if "sqlite" in async_url:
                # SQLite doesn't support connection pooling well
                engine_kwargs["poolclass"] = NullPool
            else:
                # PostgreSQL uses connection pooling
                engine_kwargs["poolclass"] = AsyncAdaptedQueuePool
                engine_kwargs["pool_size"] = 5
                engine_kwargs["max_overflow"] = 10

            self._engine = create_async_engine(async_url, **engine_kwargs)

            logger.info(f"Created async engine for {async_url.split('://')[0]}")

        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker:
        """Get or create session factory."""
        if self._session_factory is None:
            self._session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
        return self._session_factory

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get an async database session.

        Usage:
            async with db.session() as session:
                result = await session.execute(query)
        """
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def close(self) -> None:
        """Close database connections."""
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("Async database connections closed")


# Global instance
_db_manager: AsyncDatabaseManager | None = None


def get_async_db() -> AsyncDatabaseManager:
    """Get the global async database manager."""
    global _db_manager
    if _db_manager is None:
        _db_manager = AsyncDatabaseManager()
    return _db_manager


class AsyncRepository:
    """
    Async repository for database operations.

    Provides async versions of common query patterns
    for use in FastAPI async endpoints.
    """

    def __init__(self, db: AsyncDatabaseManager | None = None):
        """
        Initialize async repository.

        Args:
            db: Optional database manager (uses global if not provided)
        """
        self._db = db or get_async_db()

    async def get_all_indicators(
        self,
        tenant_id: str,
        filters: FilterParams | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get all indicator data.

        Args:
            tenant_id: Tenant identifier
            filters: Optional filter parameters

        Returns:
            List of indicator records as dictionaries
        """
        query = select(sustainability_indicators).where(
            sustainability_indicators.c.tenant_id == tenant_id
        )

        if filters:
            if filters.year:
                query = query.where(sustainability_indicators.c.year == filters.year)
            if filters.quarter:
                query = query.where(sustainability_indicators.c.quarter == filters.quarter)
            if filters.region and filters.region != "all":
                query = query.where(sustainability_indicators.c.region == filters.region)

        async with self._db.session() as session:
            result = await session.execute(query)
            rows = result.mappings().all()
            return [dict(row) for row in rows]

    async def get_latest_snapshot(
        self,
        tenant_id: str,
        filters: FilterParams | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get the latest snapshot of indicator data.

        Args:
            tenant_id: Tenant identifier
            filters: Optional filter parameters

        Returns:
            List of indicator records for latest period
        """
        async with self._db.session() as session:
            # Find latest period
            if filters is None or (filters.year is None and filters.quarter is None):
                latest_query = (
                    select(
                        sustainability_indicators.c.year,
                        sustainability_indicators.c.quarter,
                    )
                    .where(sustainability_indicators.c.tenant_id == tenant_id)
                    .order_by(
                        sustainability_indicators.c.year.desc(),
                        sustainability_indicators.c.quarter.desc(),
                    )
                    .limit(1)
                )
                result = await session.execute(latest_query)
                row = result.first()
                if not row:
                    return []
                latest_year, latest_quarter = row
            else:
                latest_year = filters.year
                latest_quarter = filters.quarter

            # Get data for that period
            query = select(sustainability_indicators).where(
                and_(
                    sustainability_indicators.c.tenant_id == tenant_id,
                    sustainability_indicators.c.year == latest_year,
                    sustainability_indicators.c.quarter == latest_quarter,
                )
            )

            if filters and filters.region and filters.region != "all":
                query = query.where(sustainability_indicators.c.region == filters.region)

            result = await session.execute(query)
            rows = result.mappings().all()
            return [dict(row) for row in rows]

    async def get_timeseries(
        self,
        tenant_id: str,
        indicator: str,
        region: str | None = None,
        years: list[int] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get time series data for an indicator.

        Args:
            tenant_id: Tenant identifier
            indicator: Indicator column name
            region: Optional region filter
            years: Optional year filter

        Returns:
            List of time series points
        """
        # Validate indicator column exists
        if not hasattr(sustainability_indicators.c, indicator):
            raise ValueError(f"Unknown indicator: {indicator}")

        indicator_col = getattr(sustainability_indicators.c, indicator)

        query = (
            select(
                sustainability_indicators.c.year,
                sustainability_indicators.c.quarter,
                sustainability_indicators.c.region,
                indicator_col.label("value"),
            )
            .where(sustainability_indicators.c.tenant_id == tenant_id)
            .order_by(
                sustainability_indicators.c.year,
                sustainability_indicators.c.quarter,
            )
        )

        if region and region != "all":
            query = query.where(sustainability_indicators.c.region == region)

        if years:
            query = query.where(sustainability_indicators.c.year.in_(years))

        async with self._db.session() as session:
            result = await session.execute(query)
            rows = result.mappings().all()
            return [dict(row) for row in rows]

    async def get_regional_comparison(
        self,
        tenant_id: str,
        year: int,
        quarter: int,
        indicator: str = "sustainability_index",
    ) -> list[dict[str, Any]]:
        """
        Get regional comparison data.

        Args:
            tenant_id: Tenant identifier
            year: Year to compare
            quarter: Quarter to compare
            indicator: Indicator to compare

        Returns:
            List of regional comparison records
        """
        if not hasattr(sustainability_indicators.c, indicator):
            raise ValueError(f"Unknown indicator: {indicator}")

        indicator_col = getattr(sustainability_indicators.c, indicator)

        query = (
            select(
                sustainability_indicators.c.region,
                indicator_col.label("value"),
            )
            .where(
                and_(
                    sustainability_indicators.c.tenant_id == tenant_id,
                    sustainability_indicators.c.year == year,
                    sustainability_indicators.c.quarter == quarter,
                )
            )
            .order_by(indicator_col.desc())
        )

        async with self._db.session() as session:
            result = await session.execute(query)
            rows = result.mappings().all()
            return [dict(row) for row in rows]

    async def get_tenant(self, tenant_id: str) -> dict[str, Any] | None:
        """Get tenant by ID."""
        query = select(tenants).where(tenants.c.id == tenant_id)

        async with self._db.session() as session:
            result = await session.execute(query)
            row = result.mappings().first()
            return dict(row) if row else None

    async def get_user(self, user_id: str) -> dict[str, Any] | None:
        """Get user by ID."""
        query = select(users).where(users.c.id == user_id)

        async with self._db.session() as session:
            result = await session.execute(query)
            row = result.mappings().first()
            return dict(row) if row else None

    async def health_check(self) -> bool:
        """
        Check database connectivity.

        Returns:
            True if database is accessible
        """
        try:
            async with self._db.session() as session:
                await session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# FastAPI dependency
async def get_async_repository() -> AsyncRepository:
    """FastAPI dependency for async repository."""
    return AsyncRepository()


# Lifespan context manager for FastAPI
@asynccontextmanager
async def database_lifespan(app):
    """
    FastAPI lifespan context manager for database.

    Usage:
        app = FastAPI(lifespan=database_lifespan)
    """
    # Startup
    db = get_async_db()
    logger.info("Database connection pool initialized")

    yield

    # Shutdown
    await db.close()
    logger.info("Database connections closed")
