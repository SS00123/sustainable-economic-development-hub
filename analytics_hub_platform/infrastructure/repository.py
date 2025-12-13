"""
Data Repository
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This module implements the Repository pattern for data access.
It provides a clean interface between business logic and database operations.
"""

from typing import Optional, List, Dict, Any
from functools import lru_cache
from datetime import datetime

import pandas as pd
from sqlalchemy import select, and_, or_
from sqlalchemy.engine import Engine

from analytics_hub_platform.infrastructure.db_init import (
    get_engine,
    sustainability_indicators,
    tenants,
    users,
)
from analytics_hub_platform.infrastructure.caching import cached, get_cache
from analytics_hub_platform.domain.models import (
    FilterParams,
    IndicatorRecord,
    Tenant,
    User,
)


class Repository:
    """
    Repository for data access operations.
    
    Provides methods to query sustainability indicators, tenants, and users.
    All methods are tenant-aware for multi-tenant support.
    """
    
    def __init__(self, engine: Optional[Engine] = None):
        """
        Initialize repository with database engine.
        
        Args:
            engine: SQLAlchemy engine instance (uses default if not provided)
        """
        self._engine = engine or get_engine()
    
    # ============================================
    # INDICATOR DATA METHODS
    # ============================================
    
    def get_all_indicators(
        self,
        tenant_id: str,
        filters: Optional[FilterParams] = None
    ) -> pd.DataFrame:
        """
        Get all indicator data as a DataFrame.
        
        Args:
            tenant_id: Tenant identifier
            filters: Optional filter parameters
            
        Returns:
            DataFrame with indicator data (columns: year, quarter, region, kpi values)
            Empty DataFrame if no data found
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
            if filters.years:
                query = query.where(sustainability_indicators.c.year.in_(filters.years))
            if filters.regions:
                query = query.where(sustainability_indicators.c.region.in_(filters.regions))
        
        with self._engine.connect() as conn:
            df = pd.read_sql(query, conn)
        
        return df
    
    def get_latest_snapshot(
        self,
        tenant_id: str,
        filters: Optional[FilterParams] = None
    ) -> pd.DataFrame:
        """
        Get the latest snapshot of indicator data.
        
        If no filters provided, returns the most recent year/quarter combination.
        
        Args:
            tenant_id: Tenant identifier
            filters: Optional filter parameters
            
        Returns:
            DataFrame with latest indicator data (single period)
            Empty DataFrame if no data found
        """
        # First, find the latest period if not specified
        if filters is None or (filters.year is None and filters.quarter is None):
            with self._engine.connect() as conn:
                result = conn.execute(
                    select(
                        sustainability_indicators.c.year,
                        sustainability_indicators.c.quarter
                    ).where(
                        sustainability_indicators.c.tenant_id == tenant_id
                    ).order_by(
                        sustainability_indicators.c.year.desc(),
                        sustainability_indicators.c.quarter.desc()
                    ).limit(1)
                )
                row = result.fetchone()
                if row:
                    latest_year, latest_quarter = row
                else:
                    return pd.DataFrame()
        else:
            latest_year = filters.year
            latest_quarter = filters.quarter
        
        # Build query for latest period
        query = select(sustainability_indicators).where(
            and_(
                sustainability_indicators.c.tenant_id == tenant_id,
                sustainability_indicators.c.year == latest_year,
                sustainability_indicators.c.quarter == latest_quarter,
            )
        )
        
        if filters and filters.region and filters.region != "all":
            query = query.where(sustainability_indicators.c.region == filters.region)
        
        with self._engine.connect() as conn:
            df = pd.read_sql(query, conn)
        
        return df
    
    def get_indicator_timeseries(
        self,
        tenant_id: str,
        indicator_id: str,
        region: Optional[str] = None,
        years: Optional[List[int]] = None
    ) -> pd.DataFrame:
        """
        Get time series data for a specific indicator.
        
        Args:
            tenant_id: Tenant identifier
            indicator_id: Column name of the indicator (e.g., 'gdp_growth')
            region: Optional region filter (e.g., 'riyadh', 'all')
            years: Optional list of years to include (e.g., [2022, 2023, 2024])
            
        Returns:
            DataFrame with time series data (columns: year, quarter, region, indicator_value)
            Empty DataFrame if indicator not found or no data
        """
        # Select only the needed columns
        columns = [
            sustainability_indicators.c.year,
            sustainability_indicators.c.quarter,
            sustainability_indicators.c.region,
            getattr(sustainability_indicators.c, indicator_id, None),
        ]
        
        # Filter out None (invalid indicator)
        columns = [c for c in columns if c is not None]
        
        query = select(*columns).where(
            sustainability_indicators.c.tenant_id == tenant_id
        )
        
        if region and region != "all":
            query = query.where(sustainability_indicators.c.region == region)
        
        if years:
            query = query.where(sustainability_indicators.c.year.in_(years))
        
        query = query.order_by(
            sustainability_indicators.c.year,
            sustainability_indicators.c.quarter
        )
        
        with self._engine.connect() as conn:
            df = pd.read_sql(query, conn)
        
        return df
    
    def get_regional_data(
        self,
        tenant_id: str,
        year: int,
        quarter: int
    ) -> pd.DataFrame:
        """
        Get data for all regions in a specific period.
        
        Args:
            tenant_id: Tenant identifier
            year: Year
            quarter: Quarter (1-4)
            
        Returns:
            DataFrame with all regions' data
        """
        query = select(sustainability_indicators).where(
            and_(
                sustainability_indicators.c.tenant_id == tenant_id,
                sustainability_indicators.c.year == year,
                sustainability_indicators.c.quarter == quarter,
            )
        ).order_by(sustainability_indicators.c.region)
        
        with self._engine.connect() as conn:
            df = pd.read_sql(query, conn)
        
        return df
    
    def get_available_periods(self, tenant_id: str) -> List[Dict[str, Any]]:
        """
        Get list of available time periods.
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            List of period dictionaries with year, quarter, and label
        """
        query = select(
            sustainability_indicators.c.year,
            sustainability_indicators.c.quarter
        ).where(
            sustainability_indicators.c.tenant_id == tenant_id
        ).distinct().order_by(
            sustainability_indicators.c.year.desc(),
            sustainability_indicators.c.quarter.desc()
        )
        
        with self._engine.connect() as conn:
            result = conn.execute(query)
            periods = []
            for row in result:
                periods.append({
                    "year": row.year,
                    "quarter": row.quarter,
                    "label": f"Q{row.quarter} {row.year}",
                })
        
        return periods
    
    def get_available_regions(self, tenant_id: str) -> List[str]:
        """
        Get list of available regions.
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            List of region names
        """
        query = select(
            sustainability_indicators.c.region
        ).where(
            sustainability_indicators.c.tenant_id == tenant_id
        ).distinct().order_by(sustainability_indicators.c.region)
        
        with self._engine.connect() as conn:
            result = conn.execute(query)
            regions = [row.region for row in result]
        
        return regions
    
    # ============================================
    # TENANT METHODS
    # ============================================
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """
        Get tenant by ID.
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Tenant model or None if not found
        """
        query = select(tenants).where(tenants.c.id == tenant_id)
        
        with self._engine.connect() as conn:
            result = conn.execute(query)
            row = result.fetchone()
            if row:
                return Tenant(
                    id=row.id,
                    name=row.name,
                    name_ar=row.name_ar,
                    country_code=row.country_code,
                    is_active=row.is_active,
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                )
        
        return None
    
    def get_all_tenants(self, active_only: bool = True) -> List[Tenant]:
        """
        Get all tenants.
        
        Args:
            active_only: If True, return only active tenants
            
        Returns:
            List of Tenant models
        """
        query = select(tenants)
        if active_only:
            query = query.where(tenants.c.is_active == True)
        
        query = query.order_by(tenants.c.name)
        
        with self._engine.connect() as conn:
            result = conn.execute(query)
            tenant_list = []
            for row in result:
                tenant_list.append(Tenant(
                    id=row.id,
                    name=row.name,
                    name_ar=row.name_ar,
                    country_code=row.country_code,
                    is_active=row.is_active,
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                ))
        
        return tenant_list
    
    # ============================================
    # USER METHODS
    # ============================================
    
    def get_user(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User identifier
            
        Returns:
            User model or None if not found
        """
        query = select(users).where(users.c.id == user_id)
        
        with self._engine.connect() as conn:
            result = conn.execute(query)
            row = result.fetchone()
            if row:
                from analytics_hub_platform.domain.models import UserRole
                return User(
                    id=row.id,
                    tenant_id=row.tenant_id,
                    email=row.email,
                    name=row.name,
                    name_ar=row.name_ar,
                    role=UserRole(row.role),
                    is_active=row.is_active,
                    preferred_language=row.preferred_language,
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                )
        
        return None
    
    def get_users_by_tenant(
        self,
        tenant_id: str,
        active_only: bool = True
    ) -> List[User]:
        """
        Get all users for a tenant.
        
        Args:
            tenant_id: Tenant identifier
            active_only: If True, return only active users
            
        Returns:
            List of User models
        """
        query = select(users).where(users.c.tenant_id == tenant_id)
        if active_only:
            query = query.where(users.c.is_active == True)
        
        query = query.order_by(users.c.name)
        
        with self._engine.connect() as conn:
            result = conn.execute(query)
            user_list = []
            from analytics_hub_platform.domain.models import UserRole
            for row in result:
                user_list.append(User(
                    id=row.id,
                    tenant_id=row.tenant_id,
                    email=row.email,
                    name=row.name,
                    name_ar=row.name_ar,
                    role=UserRole(row.role),
                    is_active=row.is_active,
                    preferred_language=row.preferred_language,
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                ))
        
        return user_list
    
    # ============================================
    # AGGREGATION METHODS
    # ============================================
    
    def get_national_aggregates(
        self,
        tenant_id: str,
        year: int,
        quarter: int
    ) -> Dict[str, float]:
        """
        Get nationally aggregated indicator values.
        
        Args:
            tenant_id: Tenant identifier
            year: Year
            quarter: Quarter (1-4)
            
        Returns:
            Dictionary of indicator names to aggregated values
        """
        df = self.get_regional_data(tenant_id, year, quarter)
        
        if len(df) == 0:
            return {}
        
        # Aggregate using mean for most indicators
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        aggregates = df[numeric_cols].mean().to_dict()
        
        # Clean up NaN values
        aggregates = {k: round(v, 2) if pd.notna(v) else None for k, v in aggregates.items()}
        
        return aggregates


# Singleton repository instance
_repository_instance: Optional[Repository] = None


@lru_cache(maxsize=1)
def get_repository() -> Repository:
    """
    Get the global repository instance.
    
    Returns:
        Repository instance
    """
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = Repository()
    return _repository_instance
