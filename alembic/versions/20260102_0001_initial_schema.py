"""
Initial schema - baseline migration

Revision ID: 0001_initial
Revises:
Create Date: 2026-01-02

Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This is the baseline migration that creates the initial database schema.
It reflects the current state of the database as defined in db_init.py.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create initial database schema."""

    # Tenants table
    op.create_table(
        "tenants",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime),
        sa.Column("updated_at", sa.DateTime),
    )

    # Users table
    op.create_table(
        "users",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("tenant_id", sa.String(50), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("name", sa.String(200)),
        sa.Column("role", sa.String(50), default="viewer"),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime),
        sa.Column("last_login", sa.DateTime),
    )
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])
    op.create_index("ix_users_email", "users", ["email"])

    # Sustainability indicators table
    op.create_table(
        "sustainability_indicators",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.String(50), nullable=False),
        sa.Column("year", sa.Integer, nullable=False),
        sa.Column("quarter", sa.Integer, nullable=False),
        sa.Column("region", sa.String(100), nullable=False),
        # Economic indicators
        sa.Column("gdp_growth", sa.Float),
        sa.Column("gdp_total", sa.Float),
        sa.Column("foreign_investment", sa.Float),
        sa.Column("export_diversity_index", sa.Float),
        sa.Column("economic_complexity", sa.Float),
        sa.Column("population", sa.Float),
        # Labor indicators
        sa.Column("unemployment_rate", sa.Float),
        sa.Column("green_jobs", sa.Float),
        sa.Column("skills_gap_index", sa.Float),
        # Social indicators
        sa.Column("social_progress_score", sa.Float),
        sa.Column("digital_readiness", sa.Float),
        sa.Column("innovation_index", sa.Float),
        # Environmental indicators
        sa.Column("co2_index", sa.Float),
        sa.Column("co2_total", sa.Float),
        sa.Column("renewable_share", sa.Float),
        sa.Column("energy_intensity", sa.Float),
        sa.Column("water_efficiency", sa.Float),
        sa.Column("waste_recycling_rate", sa.Float),
        sa.Column("forest_coverage", sa.Float),
        sa.Column("air_quality_index", sa.Float),
        # Derived indicators
        sa.Column("co2_per_gdp", sa.Float),
        sa.Column("co2_per_capita", sa.Float),
        # Quality and composite
        sa.Column("data_quality_score", sa.Float),
        sa.Column("sustainability_index", sa.Float),
        # Metadata
        sa.Column("source_system", sa.String(100)),
        sa.Column("load_timestamp", sa.DateTime),
    )
    op.create_index(
        "ix_sustainability_indicators_tenant_id", "sustainability_indicators", ["tenant_id"]
    )
    op.create_index(
        "ix_sustainability_indicators_year_quarter",
        "sustainability_indicators",
        ["year", "quarter"],
    )
    op.create_index("ix_sustainability_indicators_region", "sustainability_indicators", ["region"])

    # Audit log table
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.String(50), nullable=False),
        sa.Column("user_id", sa.String(50)),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(100)),
        sa.Column("resource_id", sa.String(100)),
        sa.Column("details", sa.Text),
        sa.Column("ip_address", sa.String(50)),
        sa.Column("user_agent", sa.String(500)),
        sa.Column("timestamp", sa.DateTime, nullable=False),
    )
    op.create_index("ix_audit_log_tenant_id", "audit_log", ["tenant_id"])
    op.create_index("ix_audit_log_timestamp", "audit_log", ["timestamp"])
    op.create_index("ix_audit_log_user_id", "audit_log", ["user_id"])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table("audit_log")
    op.drop_table("sustainability_indicators")
    op.drop_table("users")
    op.drop_table("tenants")
