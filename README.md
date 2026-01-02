# Sustainable Economic Development – Analytics Hub

**An analytics platform for economic development and sustainability indicators**

**Primary Client:** Ministry of Economy and Planning (Saudi Arabia)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

---

## Table of Contents

- [Quick Start](#-quick-start)
- [Overview](#overview)
- [Features](#-key-features)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Deployment](#-deployment)
- [Testing](#testing)
- [Architecture](#architecture)
- [Development](#development)
- [Changelog](#changelog)
- [Author](#author)

---

## 🚀 Quick Start

### ☁️ Deploy to Streamlit Community Cloud (Recommended)

1. **Fork this repository** to your GitHub account
2. **Go to** [share.streamlit.io](https://share.streamlit.io)
3. **Click** "New app" and select your forked repository
4. **Set main file path**: `streamlit_app.py`
5. **Deploy** with one click!

### 💻 Run Locally

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/analytics_hub_platform.git
cd analytics_hub_platform

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501`

### 🐳 Run with Docker

```bash
# Build the image
docker build -t analytics-hub .

# Run the Streamlit dashboard
docker run --rm -p 8501:8501 analytics-hub

# Or launch full stack with Docker Compose
docker compose up --build
```

---

## Overview

The Sustainable Economic Development Analytics Hub is a comprehensive analytics platform designed to provide executive dashboards, decision support tools, and data quality monitoring for macroeconomic, labor market, and environmental sustainability indicators.

### ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🎯 **Unified Dashboard** | Minister-level single-page view with all KPIs |
| 📊 **Executive Insights** | Sustainability index with strategic recommendations |
| 🎨 **Domain-Colored KPIs** | Color-coded indicators (Economic, Labor, Social, Environmental) |
| 📈 **Trend Analysis** | Multi-KPI time-series charts with trend lines |
| 🗺️ **Regional Comparison** | Performance across Saudi regions |
| ✅ **Data Quality** | Completeness and quality metrics |
| 🌐 **Multi-language** | English and Arabic interfaces |
| 📑 **Export** | PDF reports, PowerPoint, Excel workbooks |
| 🔒 **Role-Based Access** | Executive, Director, and Analyst views |
| 🤖 **ML Forecasting** | KPI predictions with confidence intervals |
| ♿ **WCAG 2.1 AA** | Full accessibility compliance |

---

## Project Structure

```
analytics_hub_platform/
├── streamlit_app.py            # Main Streamlit entry point
├── main_api.py                 # FastAPI entry point
├── pyproject.toml              # Project configuration
├── requirements.txt            # Python dependencies
├── alembic/                    # Database migrations
├── .streamlit/
│   └── config.toml             # Streamlit theme configuration
├── analytics_hub_platform/
│   ├── api/                    # FastAPI routers
│   ├── config/                 # Configuration & KPI catalog
│   ├── domain/                 # Business logic & ML services
│   ├── infrastructure/         # Database, auth, rate limiting
│   ├── ui/                     # Streamlit UI components
│   ├── utils/                  # Utilities & accessibility
│   └── locale/                 # Localization strings
├── tests/                      # Test suite (580+ tests)
│   └── e2e/                    # Playwright E2E tests
└── scripts/                    # Deployment & utility scripts
```

---

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Setup

```bash
# Clone repository
git clone <repository-url>
cd analytics_hub_platform

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install with optional dependencies
pip install -e ".[dev,async,migrations]"
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///analytics_hub.db` |
| `ENVIRONMENT` | Environment name | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `JWT_SECRET_KEY` | JWT secret (required in production) | - |
| `RATE_LIMIT_EXPORTS` | Max exports per minute | `10` |
| `ML_RANDOM_STATE` | Random seed for ML | `42` |

### Streamlit Secrets (Cloud Deployment)

Configure in Streamlit Cloud dashboard:

```toml
[database]
DATABASE_URL = "sqlite:///analytics_hub.db"
DEFAULT_TENANT_ID = "ministry_of_economy"

[app]
ENVIRONMENT = "production"
DEBUG = false
```

---

## API Reference

### Authentication

**Development Mode:**
```bash
curl -H "X-Tenant-ID: your_tenant_id" http://localhost:8000/api/v1/...
```

**Production Mode:**
```bash
curl -H "Authorization: Bearer <access_token>" http://localhost:8000/api/v1/...
```

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/indicators` | GET | List all indicators |
| `/api/v1/indicators/{id}` | GET | Get single indicator |
| `/api/v1/sustainability/summary` | GET | Sustainability summary |
| `/api/v1/sustainability/regions` | GET | Regional comparison |
| `/api/v1/sustainability/timeseries/{indicator}` | GET | Time series data |
| `/api/v1/data-quality` | GET | Data quality metrics |

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `year` | int | Filter by year (2015-2030) |
| `quarter` | int | Filter by quarter (1-4) |
| `region` | string | Filter by region code |
| `page` | int | Page number (default: 1) |
| `page_size` | int | Results per page (1-100) |

### Example Requests

```bash
# Get sustainability summary
curl -H "X-Tenant-ID: demo" http://localhost:8000/api/v1/sustainability/summary

# Get indicators with filters
curl -H "X-Tenant-ID: demo" \
  "http://localhost:8000/api/v1/indicators?year=2024&quarter=1&region=riyadh"

# Get time series
curl -H "X-Tenant-ID: demo" \
  http://localhost:8000/api/v1/sustainability/timeseries/sustainability_index
```

### Python SDK Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {"X-Tenant-ID": "demo_tenant"}

# Get sustainability summary
response = requests.get(f"{BASE_URL}/sustainability/summary", headers=HEADERS)
summary = response.json()
print(f"Sustainability Index: {summary['sustainability_index']}")
```

### Rate Limiting

API requests are rate-limited. Response headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1702378800
```

### Error Response Format

```json
{
    "detail": "Human-readable error message",
    "code": "ERROR_CODE",
    "correlation_id": "req-abc123"
}
```

---

## 🚀 Deployment

### Streamlit Community Cloud

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select repository: `YOUR_USERNAME/YOUR_REPO`
   - Set main file: `streamlit_app.py`
   - Click "Deploy!"

3. **Configure Secrets (Optional):**
   - Go to app settings → Secrets
   - Add configuration in TOML format

### Docker Deployment

```bash
# Using deploy script (Linux/Mac)
./scripts/deploy.sh up

# Using deploy script (Windows)
.\scripts\deploy.ps1 up

# Production with Nginx
./scripts/deploy.sh up production
```

### Required Files for Cloud

- ✅ `requirements.txt` - Python dependencies
- ✅ `packages.txt` - System dependencies
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `streamlit_app.py` - Main entry point

---

## Testing

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=analytics_hub_platform --cov-report=html

# Specific test file
pytest tests/test_ml.py -v

# Exclude E2E tests
pytest --ignore=tests/e2e
```

### Test Summary

| Category | Tests |
|----------|-------|
| Unit Tests | 580+ |
| ML Tests | 23 |
| API Tests | 30 |
| Auth Tests | 25 |
| Rate Limiting Tests | 21 |
| Async DB Tests | 17 |
| UI Component Tests | 33 |
| Model Persistence Tests | 30 |
| Accessibility Tests | 54 |
| E2E Tests (Playwright) | 16 |

### E2E Tests

```bash
# Install Playwright
pip install playwright pytest-playwright
playwright install chromium

# Run with Streamlit running
pytest tests/e2e/ -v --headed
```

---

## Architecture

### Design Principles

- **Separation of Concerns**: Clear boundaries between UI, domain, and data layers
- **Multi-tenant Ready**: Architecture supports multiple tenants
- **API-First**: All functionality exposed via FastAPI
- **Configurable**: KPIs and thresholds defined in YAML
- **Extensible**: Easy to add new KPIs and modules

### Key Modules

| Module | Purpose |
|--------|---------|
| **Sustainability** | Environmental and green economy indicators |
| **Economic Development** | GDP, investment, trade metrics |
| **Labor & Skills** | Employment and workforce indicators |
| **Data Quality** | Completeness, freshness, accuracy |
| **ML Services** | Forecasting and anomaly detection |

### Security Features

- JWT authentication with secret enforcement in production
- Rate limiting (sliding window + token bucket)
- CORS and XSRF protection
- Non-root Docker containers
- Input validation with Pydantic

### Accessibility (WCAG 2.1 AA)

- Focus indicators and keyboard navigation
- ARIA labels and live regions
- RTL support for Arabic
- High contrast mode support
- Screen reader compatibility

---

## Development

### Code Quality

```bash
# Formatting
black analytics_hub_platform/

# Linting
ruff check analytics_hub_platform/

# Type checking
mypy analytics_hub_platform/
```

### Database Migrations

```bash
# Generate migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Running Services

```bash
# Streamlit Dashboard
streamlit run streamlit_app.py

# FastAPI Backend
uvicorn main_api:app --reload --port 8000

# API Documentation
# http://localhost:8000/docs (Swagger)
# http://localhost:8000/redoc (ReDoc)
```

---

## Changelog

### Version 1.0.0 (2024-12)

**Initial Release**
- Core dashboard with unified view
- Sustainability index and KPI tracking
- Multi-language support (EN/AR)
- Export capabilities (PDF, Excel, PowerPoint)
- ML forecasting and anomaly detection

**Infrastructure Improvements**
- JWT authentication with production enforcement
- Rate limiting (sliding window algorithm)
- Async database support (aiosqlite/asyncpg)
- Alembic database migrations
- Model persistence with versioning

**Quality & Compliance**
- 580+ unit/integration tests
- WCAG 2.1 AA accessibility compliance
- OpenAPI 3.1 documentation
- Docker multi-stage builds
- CI/CD with GitHub Actions

---

## Personas

| Persona | Access Level | Features |
|---------|--------------|----------|
| **Executive** | High-level overview | Sustainability index, key KPIs, narratives |
| **Director** | Detailed analysis | Regional comparisons, trend analysis |
| **Analyst** | Full data access | Raw data, filtering, exports |

---

## Troubleshooting

### Common Issues

**Module Import Errors**
- Ensure package is in `requirements.txt`
- Reboot app from Streamlit Cloud dashboard

**Database Issues**
- SQLite creates automatically on first run
- Check logs for specific errors

**Memory Limits (Streamlit Cloud)**
- Community Cloud has 1 GB RAM limit
- Optimize data loading and use caching

**Secrets Not Found**
- Add secrets in Streamlit Cloud settings
- Use `st.secrets["key"]` to access

---

## Author

**Eng. Sultan Albuqami**

- 📱 Mobile: 0553112800
- 📧 Email: sultan_mutep@hotmail.com
- 🏛️ Organization: Ministry of Economy and Planning

---

## License

Proprietary - Ministry of Economy and Planning, Kingdom of Saudi Arabia

---

## Support

- **Documentation**: See this README
- **API Docs**: http://localhost:8000/docs
- **Issues**: GitHub Issues
- **Email**: sultan_mutep@hotmail.com
