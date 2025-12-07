# Sustainable Economic Development – Analytics Hub

**An analytics platform for economic development and sustainability indicators**

**Primary Client:** Ministry of Economy and Planning (Saudi Arabia)

---

## Overview

The Sustainable Economic Development Analytics Hub is a comprehensive analytics platform designed to provide executive dashboards, decision support tools, and data quality monitoring for macroeconomic, labor market, and environmental sustainability indicators.

### Key Features

- **Executive Dashboard**: High-level KPIs with green/amber/red status indicators
- **Director View**: Detailed analytics with regional comparisons and trend analysis
- **Analyst View**: Raw data access, data quality metrics, and export capabilities
- **Sustainability Index**: Composite 0-100 score combining environmental and development metrics
- **Multi-language Support**: English and Arabic interfaces
- **Export Capabilities**: PDF reports, PowerPoint presentations, and Excel workbooks
- **API Layer**: RESTful API for integration with other ministry systems

---

## Project Structure

```
analytics_hub_platform/
├── pyproject.toml              # Project configuration
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .gitignore                  # Git ignore rules
├── .streamlit/
│   └── config.toml             # Streamlit theme configuration
├── analytics_hub_platform/
│   ├── __init__.py
│   ├── app.py                  # Streamlit main entry point
│   ├── main_api.py             # FastAPI entry point
│   ├── config/                 # Configuration module
│   ├── domain/                 # Business logic
│   ├── infrastructure/         # Data access & utilities
│   ├── ui/                     # Streamlit UI components
│   ├── utils/                  # Utility functions
│   ├── locale/                 # Localization strings
│   └── api/                    # FastAPI routers
├── tests/                      # Test suite
└── .github/workflows/
    └── ci.yml                  # CI/CD pipeline
```

---

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd analytics_hub_platform
```

2. Create a virtual environment:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python -c "from analytics_hub_platform.infrastructure.db_init import initialize_database; initialize_database()"
```

---

## Running the Platform

### Streamlit Dashboard

```bash
streamlit run analytics_hub_platform/app.py
```

The dashboard will be available at `http://localhost:8501`

### FastAPI Backend

```bash
uvicorn analytics_hub_platform.main_api:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

---

## Usage

### Personas

The platform supports three primary personas:

1. **Executive (Minister/Leadership)**
   - High-level sustainability index and key KPIs
   - Simple, clean interface with status indicators
   - Quick narrative summaries

2. **Director (Head of Analytics)**
   - Regional comparisons and trend analysis
   - Detailed charts and visualizations
   - Period-over-period analysis

3. **Analyst**
   - Raw data access with filtering
   - Data quality metrics
   - Export capabilities (Excel, CSV)

### Navigation

- Use the sidebar to switch between views
- Global filters (Year, Quarter, Region, Language) apply across all pages
- Export buttons available on each view

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/tenants/{tenant_id}/summary` | GET | Get summary KPIs |
| `/api/v1/tenants/{tenant_id}/indicators/{indicator_id}/timeseries` | GET | Get indicator time series |
| `/api/v1/tenants/{tenant_id}/export/{format}` | GET | Export data in specified format |
| `/api/v1/health` | GET | Health check endpoint |

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///analytics_hub.db` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `RATE_LIMIT_EXPORTS` | Max exports per minute | `10` |

### KPI Catalog

KPI definitions, thresholds, and weights are configured in `config/kpi_catalog.yaml`.

---

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Formatting

```bash
black analytics_hub_platform/
ruff check analytics_hub_platform/
```

### Type Checking

```bash
mypy analytics_hub_platform/
```

---

## Architecture

### Design Principles

- **Separation of Concerns**: Clear boundaries between UI, domain logic, and data access
- **Multi-tenant Ready**: Architecture supports multiple tenants (ministries/departments)
- **API-First**: All functionality exposed via FastAPI for system integration
- **Configurable**: KPIs, thresholds, and weights defined in YAML configuration
- **Extensible**: Easy to add new KPIs, modules, and views

### Modules

- **Sustainability Module**: Environmental and green economy indicators
- **Economic Development Module**: GDP, investment, and trade metrics
- **Labor & Skills Module**: Employment and workforce indicators
- **Data Quality Module**: Completeness, freshness, and accuracy monitoring

---

## Author

**Eng. Sultan Albuqami**

- Mobile: 0553112800
- Email: sultan_mutep@hotmail.com

---

## License

Proprietary - Ministry of Economy and Planning

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2024-12 | Initial release - PoC version |
