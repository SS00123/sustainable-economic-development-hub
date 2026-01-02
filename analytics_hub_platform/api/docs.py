"""
API Documentation Configuration
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This module provides OpenAPI documentation configuration, examples,
and tag definitions for the REST API.
"""

from typing import Any

# =============================================================================
# API TAGS
# =============================================================================

API_TAGS: list[dict[str, Any]] = [
    {
        "name": "Health",
        "description": "System health checks and monitoring endpoints. Use these to verify API availability and component status.",
    },
    {
        "name": "Indicators",
        "description": """
Sustainability indicator data endpoints. Access raw indicator records
with filtering, pagination, and sorting capabilities.

**Available Indicators:**
- `sustainability_index` - Composite sustainability score (0-100)
- `co2_per_gdp` - CO2 emissions per unit GDP
- `co2_per_capita` - CO2 emissions per capita
- `renewable_energy_pct` - Renewable energy percentage
- `green_investment_pct` - Green investment percentage
- `gdp_growth` - GDP growth rate
- `employment_rate` - Employment rate
        """,
    },
    {
        "name": "Sustainability",
        "description": """
Aggregated sustainability metrics and analysis endpoints.
Get summaries, regional comparisons, and time series data.

**Key Metrics:**
- Sustainability Index trends
- Regional performance rankings
- Time series analysis
        """,
    },
    {
        "name": "Data Quality",
        "description": """
Data quality and completeness metrics. Monitor data health
and identify gaps in indicator coverage.
        """,
    },
    {
        "name": "Reference",
        "description": "Reference data for regions, time periods, and available indicators.",
    },
    {
        "name": "Metrics",
        "description": "Prometheus-compatible metrics for monitoring and alerting.",
    },
]


# =============================================================================
# REQUEST/RESPONSE EXAMPLES
# =============================================================================

INDICATOR_EXAMPLE = {
    "id": 1,
    "tenant_id": "ministry_mep",
    "year": 2024,
    "quarter": 1,
    "region": "riyadh",
    "sustainability_index": 72.5,
    "co2_per_gdp": 0.45,
    "co2_per_capita": 18.2,
    "renewable_energy_pct": 12.5,
    "green_investment_pct": 8.3,
    "gdp_growth": 4.2,
    "employment_rate": 94.5,
    "data_quality_score": 98.5,
}

INDICATOR_LIST_EXAMPLE = {
    "data": [INDICATOR_EXAMPLE],
    "total": 150,
    "page": 1,
    "page_size": 20,
    "total_pages": 8,
}

SUSTAINABILITY_SUMMARY_EXAMPLE = {
    "sustainability_index": 72.5,
    "sustainability_trend": 2.3,
    "co2_per_gdp": 0.45,
    "co2_per_capita": 18.2,
    "renewable_energy_pct": 12.5,
    "green_investment_pct": 8.3,
    "data_quality_score": 98.5,
    "period": "Q1 2024",
    "region": "all",
}

REGIONAL_COMPARISON_EXAMPLE = [
    {"region": "riyadh", "sustainability_index": 78.5, "rank": 1},
    {"region": "eastern", "sustainability_index": 75.2, "rank": 2},
    {"region": "makkah", "sustainability_index": 72.8, "rank": 3},
]

TIME_SERIES_EXAMPLE = {
    "indicator": "sustainability_index",
    "data": [
        {"period": "Q1 2023", "value": 68.5},
        {"period": "Q2 2023", "value": 70.2},
        {"period": "Q3 2023", "value": 71.8},
        {"period": "Q4 2023", "value": 72.5},
    ],
}

DATA_QUALITY_EXAMPLE = {
    "overall_score": 95.5,
    "completeness": 98.2,
    "coverage": {
        "regions_covered": 13,
        "total_regions": 13,
        "periods_covered": 8,
    },
    "by_indicator": {
        "sustainability_index": 100.0,
        "gdp_growth": 95.0,
        "employment_rate": 92.0,
    },
}

HEALTH_CHECK_EXAMPLE = {
    "status": "healthy",
    "timestamp": "2024-12-12T10:30:00Z",
    "checks": {
        "database": {
            "healthy": True,
            "message": "Connected",
            "response_time_ms": 5,
        },
        "cache": {
            "healthy": True,
            "message": "Operational",
        },
    },
}

METRICS_EXAMPLE = """# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/api/v1/indicators",status="200"} 1523
http_requests_total{method="GET",endpoint="/api/v1/sustainability/summary",status="200"} 842

# HELP http_request_duration_seconds HTTP request latency
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.1"} 1850
http_request_duration_seconds_bucket{le="0.5"} 2300
http_request_duration_seconds_bucket{le="1.0"} 2365
"""


# =============================================================================
# ERROR RESPONSE EXAMPLES
# =============================================================================

ERROR_400_EXAMPLE = {
    "detail": "Invalid quarter value. Must be between 1 and 4.",
    "error_code": "VALIDATION_ERROR",
    "correlation_id": "req-abc123-def456",
}

ERROR_401_EXAMPLE = {
    "detail": "Authentication required",
    "error_code": "UNAUTHORIZED",
}

ERROR_403_EXAMPLE = {
    "detail": "Insufficient permissions for this resource",
    "error_code": "FORBIDDEN",
}

ERROR_404_EXAMPLE = {
    "detail": "Indicator record not found",
    "error_code": "NOT_FOUND",
}

ERROR_429_EXAMPLE = {
    "detail": "Rate limit exceeded. Try again in 60 seconds.",
    "error_code": "RATE_LIMITED",
    "retry_after": 60,
}

ERROR_500_EXAMPLE = {
    "detail": "An unexpected error occurred",
    "error_code": "INTERNAL_ERROR",
    "correlation_id": "req-abc123-def456",
}


# =============================================================================
# OPENAPI CUSTOMIZATION
# =============================================================================

OPENAPI_DESCRIPTION = """
# Sustainable Economic Development Analytics Hub API

REST API for accessing sustainability indicators, KPI data, and analytics
for the Ministry of Economy and Planning, Kingdom of Saudi Arabia.

## Overview

This API provides programmatic access to the Analytics Hub's data and features:

- **Real-time Indicators**: Access the latest sustainability and economic indicators
- **Historical Data**: Query historical trends and time series
- **Regional Analysis**: Compare performance across Saudi regions
- **Data Quality**: Monitor data completeness and quality metrics

## Quick Start

### 1. Get Current Sustainability Summary
```bash
curl -H "X-Tenant-ID: demo_tenant" \\
     https://api.analytics-hub.gov.sa/api/v1/sustainability/summary
```

### 2. Query Indicators with Filters
```bash
curl -H "X-Tenant-ID: demo_tenant" \\
     "https://api.analytics-hub.gov.sa/api/v1/indicators?year=2024&quarter=1&region=riyadh"
```

### 3. Get Regional Comparison
```bash
curl -H "X-Tenant-ID: demo_tenant" \\
     https://api.analytics-hub.gov.sa/api/v1/sustainability/regions
```

## Authentication

**Development**: Use HTTP headers for context:
- `X-Tenant-ID`: Tenant identifier (required)
- `X-User-ID`: User identifier (optional)
- `X-Correlation-ID`: Request correlation ID (optional, auto-generated if not provided)

**Production**: Integrated with Ministry SSO via OAuth 2.0 / OIDC.

## Rate Limiting

| Tier | Requests/Minute | Burst |
|------|-----------------|-------|
| Standard | 60 | 10 |
| Premium | 300 | 50 |
| Internal | 1000 | 100 |

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Maximum requests per window
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Window reset timestamp

## Error Handling

All errors follow a consistent format:
```json
{
    "detail": "Human-readable error message",
    "error_code": "MACHINE_READABLE_CODE",
    "correlation_id": "req-abc123-def456"
}
```

Common error codes:
- `VALIDATION_ERROR` - Invalid input parameters
- `NOT_FOUND` - Resource not found
- `UNAUTHORIZED` - Authentication required
- `FORBIDDEN` - Insufficient permissions
- `RATE_LIMITED` - Too many requests
- `INTERNAL_ERROR` - Server error

## Versioning

The API uses URL path versioning (`/api/v1/`). Breaking changes will increment
the version number. Deprecated endpoints include a `Deprecation` header.

## Support

For API support or to report issues:
- Email: sultan_mutep@hotmail.com
- Documentation: https://docs.analytics-hub.gov.sa
"""


def get_openapi_config() -> dict[str, Any]:
    """Get OpenAPI configuration for FastAPI."""
    return {
        "title": "Sustainable Economic Development Analytics Hub API",
        "description": OPENAPI_DESCRIPTION,
        "version": "1.0.0",
        "openapi_tags": API_TAGS,
        "contact": {
            "name": "API Support",
            "email": "sultan_mutep@hotmail.com",
            "url": "https://docs.analytics-hub.gov.sa",
        },
        "license_info": {
            "name": "Proprietary - Ministry of Economy and Planning",
            "url": "https://ministry.gov.sa/terms",
        },
        "servers": [
            {
                "url": "https://api.analytics-hub.gov.sa",
                "description": "Production Server",
            },
            {
                "url": "https://staging-api.analytics-hub.gov.sa",
                "description": "Staging Server",
            },
            {
                "url": "http://localhost:8000",
                "description": "Local Development",
            },
        ],
    }
