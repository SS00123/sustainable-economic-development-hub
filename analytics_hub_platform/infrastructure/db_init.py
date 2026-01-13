"""
Database Initialization
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This module handles:
- Database schema creation
- Synthetic data generation for PoC
- Database engine management

The schema is designed to be easily migrated to PostgreSQL
for production deployment.
"""

import random
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    text,
)
from sqlalchemy.engine import Engine

from analytics_hub_platform.infrastructure.settings import get_settings


def utc_now() -> datetime:
    """Return current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


# Database metadata
metadata = MetaData()


# ============================================
# TABLE DEFINITIONS
# ============================================

# Main indicators table
sustainability_indicators = Table(
    "sustainability_indicators",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("tenant_id", String(50), nullable=False, index=True),
    Column("year", Integer, nullable=False),
    Column("quarter", Integer, nullable=False),
    Column("region", String(100), nullable=False),
    # Economic indicators
    Column("gdp_growth", Float),
    Column("gdp_total", Float),
    Column("foreign_investment", Float),
    Column("export_diversity_index", Float),
    Column("economic_complexity", Float),
    Column("population", Float),
    # Labor indicators
    Column("unemployment_rate", Float),
    Column("green_jobs", Float),
    Column("skills_gap_index", Float),
    # Social indicators
    Column("social_progress_score", Float),
    Column("digital_readiness", Float),
    Column("innovation_index", Float),
    # Environmental indicators
    Column("co2_index", Float),
    Column("co2_total", Float),
    Column("renewable_share", Float),
    Column("energy_intensity", Float),
    Column("water_efficiency", Float),
    Column("waste_recycling_rate", Float),
    Column("forest_coverage", Float),
    Column("air_quality_index", Float),
    # Derived indicators
    Column("co2_per_gdp", Float),
    Column("co2_per_capita", Float),
    # Quality and composite
    Column("data_quality_score", Float),
    Column("sustainability_index", Float),
    # Metadata
    Column("source_system", String(100)),
    Column("load_timestamp", DateTime, default=utc_now),
    Column("load_batch_id", String(50)),
    # Indexes for common queries
    Index("idx_tenant_year_quarter", "tenant_id", "year", "quarter"),
    Index("idx_tenant_region", "tenant_id", "region"),
)


# Tenants table (for multi-tenant support)
tenants = Table(
    "tenants",
    metadata,
    Column("id", String(50), primary_key=True),
    Column("name", String(200), nullable=False),
    Column("name_ar", String(200)),
    Column("country_code", String(10), default="SA"),
    Column("is_active", Boolean, default=True),
    Column("created_at", DateTime, default=utc_now),
    Column("updated_at", DateTime, default=utc_now, onupdate=utc_now),
    Column("config_overrides", Text),  # JSON string for tenant-specific config
)


# Users table (for RBAC - currently mocked)
users = Table(
    "users",
    metadata,
    Column("id", String(50), primary_key=True),
    Column("tenant_id", String(50), nullable=False, index=True),
    Column("email", String(200), nullable=False, unique=True),
    Column("name", String(200), nullable=False),
    Column("name_ar", String(200)),
    Column("role", String(50), nullable=False, default="viewer"),
    Column("is_active", Boolean, default=True),
    Column("preferred_language", String(10), default="en"),
    Column("created_at", DateTime, default=utc_now),
    Column("updated_at", DateTime, default=utc_now, onupdate=utc_now),
    # Extension Point: Add SSO-related columns here
    # Column("sso_id", String(200)),
    # Column("last_login", DateTime),
)


# Audit log table (for governance)
audit_log = Table(
    "audit_log",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("timestamp", DateTime, default=utc_now),
    Column("tenant_id", String(50)),
    Column("user_id", String(50)),
    Column("action", String(100), nullable=False),
    Column("resource_type", String(100)),
    Column("resource_id", String(200)),
    Column("details", Text),  # JSON string with action details
    Column("ip_address", String(50)),
    Index("idx_audit_tenant_timestamp", "tenant_id", "timestamp"),
)


# ============================================
# ENGINE MANAGEMENT
# ============================================

_engine: Engine | None = None
_engine_lock = None  # Lazy initialization for threading


def _get_engine_lock():
    """Get or create the engine lock (lazy init to avoid import issues)."""
    global _engine_lock
    if _engine_lock is None:
        import threading

        _engine_lock = threading.Lock()
    return _engine_lock


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """
    Get or create the database engine with connection pooling.

    Connection Pool Configuration:
    - pool_size: Number of connections to keep open (default: 5)
    - max_overflow: Extra connections allowed beyond pool_size (default: 10)
    - pool_timeout: Seconds to wait for connection from pool (default: 30)
    - pool_recycle: Seconds before connection is recycled (default: 1800 = 30 min)
    - pool_pre_ping: Test connections before use (default: True)

    Returns:
        SQLAlchemy Engine instance
    """
    global _engine

    with _get_engine_lock():
        if _engine is None:
            settings = get_settings()

            # Determine if SQLite (no pooling) or production DB
            is_sqlite = "sqlite" in settings.database_url.lower()

            if is_sqlite:
                # SQLite doesn't support connection pooling well
                _engine = create_engine(
                    settings.database_url,
                    echo=settings.database_echo,
                    connect_args={"check_same_thread": False},
                )
            else:
                # Production database with connection pooling
                _engine = create_engine(
                    settings.database_url,
                    echo=settings.database_echo,
                    pool_size=getattr(settings, "db_pool_size", 5),
                    max_overflow=getattr(settings, "db_max_overflow", 10),
                    pool_timeout=getattr(settings, "db_pool_timeout", 30),
                    pool_recycle=getattr(settings, "db_pool_recycle", 1800),
                    pool_pre_ping=True,  # Test connections before use
                )

        return _engine


def check_database_health() -> dict[str, Any]:
    """
    Check database connectivity and pool status.

    Returns:
        Dictionary with health check results
    """
    result = {
        "status": "unknown",
        "connected": False,
        "pool_size": 0,
        "checked_out": 0,
        "overflow": 0,
        "message": "",
    }

    try:
        engine = get_engine()

        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            result["connected"] = True

        # Get pool status (if pooled)
        pool = engine.pool
        size_fn = getattr(pool, "size", None)
        if callable(size_fn):
            result["pool_size"] = size_fn()
        checkedout_fn = getattr(pool, "checkedout", None)
        if callable(checkedout_fn):
            result["checked_out"] = checkedout_fn()
        overflow_fn = getattr(pool, "overflow", None)
        if callable(overflow_fn):
            result["overflow"] = overflow_fn()

        result["status"] = "healthy"
        result["message"] = "Database connection successful"

    except Exception as e:
        result["status"] = "unhealthy"
        result["message"] = str(e)

    return result


def dispose_engine() -> None:
    """
    Dispose of the engine and all pooled connections.

    Call this during shutdown or when reconfiguring the database.
    """
    global _engine

    with _get_engine_lock():
        if _engine is not None:
            _engine.dispose()
            _engine = None
            # Clear the lru_cache
            get_engine.cache_clear()


def create_tables() -> None:
    """Create all database tables."""
    engine = get_engine()
    metadata.create_all(engine)


# ============================================
# SYNTHETIC DATA GENERATION
# ============================================

# Import from centralized constants
from analytics_hub_platform.config.constants import (
    REGION_PROFILES,
)
from analytics_hub_platform.config.constants import (
    SAUDI_REGIONS as REGIONS,
)


def _generate_with_trend(
    base: float, year: int, base_year: int = 2020, annual_growth: float = 0.02, noise: float = 0.1
) -> float:
    """Generate value with trend and noise."""
    years_from_base = year - base_year
    trend = base * ((1 + annual_growth) ** years_from_base)
    noise_factor = 1 + random.uniform(-noise, noise)
    return trend * noise_factor


def generate_synthetic_data(tenant_id: str = "mep-sa-001") -> list:
    """
    Generate realistic synthetic data for the PoC.

    Creates data for:
    - Years: 2020-2024
    - All 4 quarters per year
    - All 13 Saudi regions

    Returns:
        List of dictionaries ready for database insertion
    """
    random.seed(42)  # For reproducibility

    records = []
    batch_id = f"init-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    years = [2020, 2021, 2022, 2023, 2024, 2025, 2026]
    quarters = [1, 2, 3, 4]

    for year in years:
        for quarter in quarters:
            for region in REGIONS:
                profile = REGION_PROFILES[region]

                # Economic indicators with trends
                gdp_total = _generate_with_trend(
                    profile["gdp_base"], year, annual_growth=0.04, noise=0.05
                )
                gdp_growth = random.uniform(2.0, 6.0) + (year - 2020) * 0.3
                gdp_growth += random.uniform(-1.0, 1.0)  # Quarterly noise

                foreign_investment = _generate_with_trend(
                    profile["gdp_base"] * 0.02, year, annual_growth=0.08, noise=0.15
                )

                export_diversity = 40 + (year - 2020) * 3 + random.uniform(-5, 5)
                export_diversity = min(100, max(0, export_diversity))

                economic_complexity = -0.5 + (year - 2020) * 0.15 + random.uniform(-0.1, 0.1)

                population = profile["population"] * (1.02 ** (year - 2020))
                population += random.uniform(-0.05, 0.05)

                # Labor indicators
                unemployment_base = 8.0 if profile["urban"] else 10.0
                unemployment_rate = unemployment_base - (year - 2020) * 0.5 + random.uniform(-1, 1)
                unemployment_rate = max(3, min(15, unemployment_rate))

                green_jobs = _generate_with_trend(
                    50 if profile["urban"] else 20, year, annual_growth=0.15, noise=0.1
                )

                skills_gap = 50 - (year - 2020) * 3 + random.uniform(-5, 5)
                skills_gap = max(10, min(80, skills_gap))

                # Social indicators
                social_progress = 60 + (year - 2020) * 2 + random.uniform(-3, 3)
                social_progress = min(100, max(0, social_progress))

                digital_readiness = 55 + (year - 2020) * 4 + random.uniform(-5, 5)
                digital_readiness = min(100, max(0, digital_readiness))
                if profile["urban"]:
                    digital_readiness += 10

                innovation_index = 35 + (year - 2020) * 3 + random.uniform(-4, 4)
                innovation_index = min(100, max(0, innovation_index))

                # Environmental indicators
                co2_index = 95 - (year - 2020) * 2 + random.uniform(-5, 5)
                co2_index = max(70, min(120, co2_index))

                co2_total = gdp_total * 0.0003 * (co2_index / 100)

                renewable_share = 5 + (year - 2020) * 4 + random.uniform(-2, 2)
                renewable_share = max(0, min(50, renewable_share))

                energy_intensity_val = 8 - (year - 2020) * 0.3 + random.uniform(-0.5, 0.5)
                energy_intensity_val = max(3, min(15, energy_intensity_val))

                water_efficiency = 50 + (year - 2020) * 3 + random.uniform(-5, 5)
                water_efficiency = min(100, max(0, water_efficiency))

                waste_recycling = 15 + (year - 2020) * 4 + random.uniform(-3, 3)
                waste_recycling = max(0, min(60, waste_recycling))

                forest_coverage = 2.0 + (year - 2020) * 0.2 + random.uniform(-0.3, 0.3)
                forest_coverage = max(0.5, min(10, forest_coverage))

                air_quality = 70 - (year - 2020) * 3 + random.uniform(-10, 10)
                air_quality = max(30, min(150, air_quality))

                # Derived indicators
                co2_per_gdp_val = (co2_total * 1_000_000) / gdp_total if gdp_total > 0 else None
                co2_per_capita_val = co2_total / population if population > 0 else None

                # Data quality score
                data_quality = 75 + (year - 2020) * 3 + random.uniform(-5, 5)
                data_quality = min(100, max(50, data_quality))

                # Sustainability index (simplified calculation for synthetic data)
                sustainability = (
                    (100 - co2_index + 70) / 2 * 0.15  # Normalized CO2 (inverse)
                    + renewable_share * 0.15
                    + (100 - energy_intensity_val * 10) * 0.10
                    + water_efficiency * 0.10
                    + waste_recycling * 1.67 * 0.10  # Scale to ~100
                    + (100 - air_quality) * 0.10
                    + forest_coverage * 10 * 0.05
                    + min(green_jobs, 100) * 0.10
                    + export_diversity * 0.05
                    + (economic_complexity + 2) * 25 * 0.05
                )
                sustainability = max(0, min(100, sustainability))

                record = {
                    "tenant_id": tenant_id,
                    "year": year,
                    "quarter": quarter,
                    "region": region,
                    "gdp_growth": round(gdp_growth, 2),
                    "gdp_total": round(gdp_total, 2),
                    "foreign_investment": round(foreign_investment, 2),
                    "export_diversity_index": round(export_diversity, 2),
                    "economic_complexity": round(economic_complexity, 3),
                    "population": round(population, 3),
                    "unemployment_rate": round(unemployment_rate, 2),
                    "green_jobs": round(green_jobs, 1),
                    "skills_gap_index": round(skills_gap, 2),
                    "social_progress_score": round(social_progress, 2),
                    "digital_readiness": round(digital_readiness, 2),
                    "innovation_index": round(innovation_index, 2),
                    "co2_index": round(co2_index, 2),
                    "co2_total": round(co2_total, 2),
                    "renewable_share": round(renewable_share, 2),
                    "energy_intensity": round(energy_intensity_val, 2),
                    "water_efficiency": round(water_efficiency, 2),
                    "waste_recycling_rate": round(waste_recycling, 2),
                    "forest_coverage": round(forest_coverage, 2),
                    "air_quality_index": round(air_quality, 2),
                    "co2_per_gdp": round(co2_per_gdp_val, 2) if co2_per_gdp_val else None,
                    "co2_per_capita": round(co2_per_capita_val, 2) if co2_per_capita_val else None,
                    "data_quality_score": round(data_quality, 2),
                    "sustainability_index": round(sustainability, 2),
                    "source_system": "synthetic_data_generator",
                    "load_timestamp": datetime.now(),
                    "load_batch_id": batch_id,
                }

                records.append(record)

    return records


def generate_mock_users(tenant_id: str = "mep-sa-001") -> list:
    """Generate mock users for demonstration."""
    return [
        {
            "id": "user-001",
            "tenant_id": tenant_id,
            "email": "minister@mep.gov.sa",
            "name": "His Excellency the Minister",
            "name_ar": "معالي الوزير",
            "role": "minister",
            "is_active": True,
            "preferred_language": "ar",
        },
        {
            "id": "user-002",
            "tenant_id": tenant_id,
            "email": "director.analytics@mep.gov.sa",
            "name": "Director of Analytics",
            "name_ar": "مدير التحليلات",
            "role": "director",
            "is_active": True,
            "preferred_language": "en",
        },
        {
            "id": "user-003",
            "tenant_id": tenant_id,
            "email": "senior.analyst@mep.gov.sa",
            "name": "Senior Data Analyst",
            "name_ar": "محلل بيانات أول",
            "role": "analyst",
            "is_active": True,
            "preferred_language": "en",
        },
        {
            "id": "user-004",
            "tenant_id": tenant_id,
            "email": "admin@mep.gov.sa",
            "name": "System Administrator",
            "name_ar": "مدير النظام",
            "role": "admin",
            "is_active": True,
            "preferred_language": "en",
        },
    ]


def initialize_database(force_recreate: bool = False) -> None:
    """
    Initialize the database with schema and synthetic data.

    Args:
        force_recreate: If True, drop and recreate all tables
    """
    engine = get_engine()

    if force_recreate:
        metadata.drop_all(engine)

    # Create tables
    create_tables()

    # Check if data already exists
    with engine.connect() as conn:
        result = conn.execute(sustainability_indicators.select().limit(1))
        if result.fetchone() is not None:
            print("Database already initialized with data.")
            return

    # Insert default tenant
    with engine.connect() as conn:
        settings = get_settings()
        conn.execute(
            tenants.insert().values(
                id=settings.default_tenant_id,
                name=settings.default_tenant_name,
                name_ar="وزارة الاقتصاد والتخطيط",
                country_code="SA",
                is_active=True,
            )
        )
        conn.commit()

    # Insert mock users
    mock_users = generate_mock_users()
    with engine.connect() as conn:
        for user in mock_users:
            conn.execute(users.insert().values(**user))
        conn.commit()

    # Generate and insert synthetic data
    print("Generating synthetic data...")
    records = generate_synthetic_data()

    print(f"Inserting {len(records)} records...")
    with engine.connect() as conn:
        for record in records:
            conn.execute(sustainability_indicators.insert().values(**record))
        conn.commit()

    print("Database initialization complete.")


if __name__ == "__main__":
    # Allow running directly to initialize database
    initialize_database(force_recreate=True)
