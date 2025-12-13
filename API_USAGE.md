# API Usage Guide

## Sustainable Economic Development Analytics Hub API

This guide provides examples for using the Analytics Hub REST API.

## Table of Contents

- [Authentication](#authentication)
- [Quick Start](#quick-start)
- [Indicators API](#indicators-api)
- [Sustainability API](#sustainability-api)
- [Data Quality API](#data-quality-api)
- [Reference API](#reference-api)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)

---

## Authentication

### Development Mode

For development and testing, use HTTP headers:

```bash
# Required: Tenant identifier
-H "X-Tenant-ID: your_tenant_id"

# Optional: User identifier
-H "X-User-ID: user@example.com"

# Optional: Correlation ID for request tracing
-H "X-Correlation-ID: my-request-123"
```

### Production Mode

Production uses OAuth 2.0 / OpenID Connect via Ministry SSO.

```bash
# Bearer token authentication
-H "Authorization: Bearer <access_token>"
```

---

## Quick Start

### Check API Health

```bash
curl http://localhost:8000/health
```

Response:
```json
{
    "status": "healthy",
    "timestamp": "2024-12-12T10:30:00Z"
}
```

### Get Current Sustainability Summary

```bash
curl -H "X-Tenant-ID: demo_tenant" \
     http://localhost:8000/api/v1/sustainability/summary
```

Response:
```json
{
    "sustainability_index": 72.5,
    "sustainability_trend": 2.3,
    "co2_per_gdp": 0.45,
    "co2_per_capita": 18.2,
    "renewable_energy_pct": 12.5,
    "green_investment_pct": 8.3,
    "data_quality_score": 98.5,
    "period": "Q1 2024",
    "region": "all"
}
```

---

## Indicators API

### List All Indicators

```bash
# Basic request
curl -H "X-Tenant-ID: demo_tenant" \
     http://localhost:8000/api/v1/indicators

# With pagination
curl -H "X-Tenant-ID: demo_tenant" \
     "http://localhost:8000/api/v1/indicators?page=1&page_size=20"

# With filters
curl -H "X-Tenant-ID: demo_tenant" \
     "http://localhost:8000/api/v1/indicators?year=2024&quarter=1&region=riyadh"
```

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `year` | int | Filter by year (2015-2030) | All years |
| `quarter` | int | Filter by quarter (1-4) | All quarters |
| `region` | string | Filter by region code | All regions |
| `page` | int | Page number | 1 |
| `page_size` | int | Results per page (1-100) | 20 |

**Response:**
```json
{
    "data": [
        {
            "id": 1,
            "tenant_id": "demo_tenant",
            "year": 2024,
            "quarter": 1,
            "region": "riyadh",
            "sustainability_index": 72.5,
            "co2_per_gdp": 0.45,
            "renewable_energy_pct": 12.5,
            "gdp_growth": 4.2
        }
    ],
    "total": 150,
    "page": 1,
    "page_size": 20,
    "total_pages": 8
}
```

### Get Single Indicator

```bash
curl -H "X-Tenant-ID: demo_tenant" \
     http://localhost:8000/api/v1/indicators/1
```

---

## Sustainability API

### Get Sustainability Summary

```bash
# All regions
curl -H "X-Tenant-ID: demo_tenant" \
     http://localhost:8000/api/v1/sustainability/summary

# Specific region
curl -H "X-Tenant-ID: demo_tenant" \
     "http://localhost:8000/api/v1/sustainability/summary?region=riyadh"

# Specific period
curl -H "X-Tenant-ID: demo_tenant" \
     "http://localhost:8000/api/v1/sustainability/summary?year=2024&quarter=1"
```

### Get Regional Comparison

Compare sustainability index across all regions:

```bash
curl -H "X-Tenant-ID: demo_tenant" \
     http://localhost:8000/api/v1/sustainability/regions
```

**Response:**
```json
[
    {"region": "riyadh", "sustainability_index": 78.5, "rank": 1},
    {"region": "eastern", "sustainability_index": 75.2, "rank": 2},
    {"region": "makkah", "sustainability_index": 72.8, "rank": 3}
]
```

### Get Time Series Data

```bash
# Sustainability index over time
curl -H "X-Tenant-ID: demo_tenant" \
     http://localhost:8000/api/v1/sustainability/timeseries/sustainability_index

# GDP growth for specific region
curl -H "X-Tenant-ID: demo_tenant" \
     "http://localhost:8000/api/v1/sustainability/timeseries/gdp_growth?region=riyadh"
```

**Available Indicators:**
- `sustainability_index`
- `co2_per_gdp`
- `co2_per_capita`
- `renewable_energy_pct`
- `green_investment_pct`
- `gdp_growth`

**Response:**
```json
{
    "indicator": "sustainability_index",
    "data": [
        {"period": "Q1 2023", "value": 68.5},
        {"period": "Q2 2023", "value": 70.2},
        {"period": "Q3 2023", "value": 71.8},
        {"period": "Q4 2023", "value": 72.5}
    ]
}
```

---

## Data Quality API

### Get Data Quality Metrics

```bash
curl -H "X-Tenant-ID: demo_tenant" \
     http://localhost:8000/api/v1/data-quality
```

**Response:**
```json
{
    "completeness": 98.2,
    "avg_quality_score": 95.5,
    "records_count": 1560,
    "last_update": "2024-12-12T08:00:00Z",
    "missing_by_kpi": {
        "employment_rate": 12,
        "green_investment_pct": 5
    }
}
```

---

## Reference API

### Get Available Regions

```bash
curl -H "X-Tenant-ID: demo_tenant" \
     http://localhost:8000/api/v1/reference/regions
```

**Response:**
```json
["riyadh", "makkah", "madinah", "eastern", "qassim", "asir", "tabuk", "hail", "northern_borders", "jazan", "najran", "baha", "jouf"]
```

### Get Available Years

```bash
curl -H "X-Tenant-ID: demo_tenant" \
     http://localhost:8000/api/v1/reference/years
```

**Response:**
```json
[2020, 2021, 2022, 2023, 2024]
```

---

## Error Handling

All errors return a consistent JSON format:

```json
{
    "detail": "Human-readable error message",
    "code": "ERROR_CODE",
    "correlation_id": "req-abc123"
}
```

### Common Error Codes

| Status | Code | Description |
|--------|------|-------------|
| 400 | `VALIDATION_ERROR` | Invalid request parameters |
| 401 | `UNAUTHORIZED` | Authentication required |
| 403 | `FORBIDDEN` | Insufficient permissions |
| 404 | `NOT_FOUND` | Resource not found |
| 429 | `RATE_LIMITED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Server error |

### Example Error Response

```bash
curl -H "X-Tenant-ID: demo_tenant" \
     "http://localhost:8000/api/v1/indicators?quarter=5"
```

```json
{
    "detail": "Invalid quarter value. Must be between 1 and 4.",
    "code": "VALIDATION_ERROR",
    "correlation_id": "req-abc123-def456"
}
```

---

## Rate Limiting

API requests are rate-limited. Headers indicate your limit status:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1702378800
```

When rate limited (HTTP 429):

```json
{
    "detail": "Rate limit exceeded. Try again in 60 seconds.",
    "code": "RATE_LIMITED",
    "retry_after": 60
}
```

---

## Python Examples

### Using requests library

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {"X-Tenant-ID": "demo_tenant"}

# Get sustainability summary
response = requests.get(
    f"{BASE_URL}/sustainability/summary",
    headers=HEADERS
)
summary = response.json()
print(f"Sustainability Index: {summary['sustainability_index']}")

# Get indicators with filters
response = requests.get(
    f"{BASE_URL}/indicators",
    headers=HEADERS,
    params={"year": 2024, "quarter": 1, "region": "riyadh"}
)
indicators = response.json()
for indicator in indicators["data"]:
    print(f"{indicator['region']}: {indicator['sustainability_index']}")
```

### Using httpx (async)

```python
import asyncio
import httpx

async def get_regional_comparison():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/v1/sustainability/regions",
            headers={"X-Tenant-ID": "demo_tenant"}
        )
        return response.json()

# Run async
regions = asyncio.run(get_regional_comparison())
for region in regions:
    print(f"#{region['rank']} {region['region']}: {region['sustainability_index']}")
```

---

## OpenAPI Specification

The full OpenAPI specification is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Support

- **Email**: sultan_mutep@hotmail.com
- **Documentation**: https://docs.analytics-hub.gov.sa
- **Issue Tracker**: https://github.com/ministry/analytics-hub/issues
