# Changelog

All notable changes to the Sustainable Economic Development Analytics Hub will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Phase 7: Advanced analytics capabilities (forecasting, anomaly detection) integrated into KPIs/Trends
- Phase 8: Insight Engine (rules registry, explanations)
- Phase 9: Maturity (release cadence, final verification)

### Changed
- Streamlit navigation: Data Management merged into the Data page (Management tab)
- In-app documentation moved to the Help page (`pages/06_Help.py`)

### Removed
- Legacy standalone pages removed from navigation: `pages/08_Data_Management.py`, `pages/09_Documentation.py`

---

## [1.5.0] - 2026-01-05

### Added
- **Phase 6: Governance**
  - KPI Register (`kpi_register.yaml`) with 13 KPIs across 4 pillars
  - Governance documentation (`GOVERNANCE.md`)
  - Compliance checker module (`compliance_checker.py`)
  - This CHANGELOG file

### Changed
- Enhanced data quality checks to align with KPI register thresholds

---

## [1.4.0] - 2026-01-05

### Added
- **Phase 5: Observability + QoS**
  - Telemetry module (`infrastructure/telemetry.py`)
    - Event capture for page views, exports, presets, filters
    - TimingContext context manager for performance tracking
    - @timed decorator for function timing
    - FILE and LOG backend support
  - Operations Runbook (`OPS_RUNBOOK.md`) - 446 lines
  - Performance Budgets document (`PERFORMANCE_BUDGETS.md`) - 327 lines
  - 35 telemetry tests

### Changed
- Updated Diagnostics page to include telemetry statistics

---

## [1.3.0] - 2026-01-05

### Added
- **Phase 4: Adoption + Sharing**
  - Shareable links module (`ui/shareable_links.py`)
    - ViewState dataclass for URL state management
    - PresetManager with 5 default presets including Arabic view
    - Query parameter and encoded state URL generation
  - Export utilities (`utils/export_utils.py`)
    - CSV export with UTF-8-sig BOM for Excel compatibility
    - PNG export with kaleido (graceful fallback)
    - PDF Executive Brief with reportlab
  - Documentation page (`pages/09_Documentation.py`)
    - About, Methodology, Data Sources, Glossary, FAQ tabs
  - 39 tests for Phase 4 components

### Changed
- Dashboard now supports shareable URLs with filter state

---

## [1.2.0] - 2026-01-05

### Added
- **Phase 3: Go-Live + Data Readiness**
  - Data Contract document (`DATA_CONTRACT.md`)
  - Diagnostics page (`pages/07_Diagnostics.py`)
    - System version and environment info
    - Database connectivity check
    - Smoke tests with pass/fail status
    - Cache statistics
  - Data Management page (`pages/08_Data_Management.py`)
    - CSV/Excel file upload
    - Data quality report display
  - Data ingestion module (`infrastructure/data_ingestion.py`)
    - 668 lines of CSV/Excel parsing and validation
    - IngestionResult with success/error tracking
  - Data quality module (`infrastructure/data_quality.py`)
    - 9 quality check types
    - DataQualityReport generation
    - 551 lines of DQ logic
  - Test fixtures: sample_good.csv, sample_bad.csv, sample_missing_columns.csv
  - 55 tests for data ingestion and quality

### Fixed
- 8 instances of `datetime.UTC` changed to `timezone.utc` for Python 3.10 compatibility
  - `api/routers.py`
  - `infrastructure/audit.py`
  - `infrastructure/observability.py` (4 instances)
  - `infrastructure/dataframe_adapter.py` (2 instances)

---

## [1.1.0] - 2026-01-04

### Added
- **Phase 2: Productionization**
  - Dockerfile for containerized deployment
  - Docker Compose configuration
  - GitHub Actions CI/CD workflow (`.github/workflows/ci.yml`)
  - 35 pytest tests covering core functionality
  - pyproject.toml with tool configurations

### Changed
- Refactored page files to use ASCII-compatible names
- Replaced deprecated Streamlit components

---

## [1.0.0] - 2026-01-04

### Added
- **Phase 1: Core Dashboard Refactoring**
  - Streamlit application entry point (`streamlit_app.py`)
  - Multi-page navigation structure
  - Dashboard page with KPI cards and visualizations
  - KPIs page with detailed metrics
  - Trends page with historical analysis
  - Data page with raw data display
  - Advanced Analytics page
  - Settings page
  - Dark theme CSS components
  - RTL (Right-to-Left) language support for Arabic
  - Custom HTML rendering utilities
  - Theme configuration module
  - SQLite database with SQLAlchemy ORM
  - Alembic migrations
  - Synthetic data generator

### Technical
- Python 3.11+ support
- Streamlit 1.28+ compatibility
- pandas 2.0+ for data manipulation
- Plotly for interactive visualizations
- SQLAlchemy 2.0 for database operations

---

## Version Numbering

This project uses [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes, breaking changes
- **MINOR**: New functionality in a backward-compatible manner
- **PATCH**: Backward-compatible bug fixes

### Version History Summary

| Version | Date | Phase | Key Changes |
|---------|------|-------|-------------|
| 1.5.0 | 2026-01-05 | 6 | Governance, KPI Register, Compliance |
| 1.4.0 | 2026-01-05 | 5 | Telemetry, Ops Runbook, Performance Budgets |
| 1.3.0 | 2026-01-05 | 4 | Shareable Links, Export, Documentation |
| 1.2.0 | 2026-01-05 | 3 | Data Ingestion, DQ, Diagnostics |
| 1.1.0 | 2026-01-04 | 2 | Docker, CI/CD, Tests |
| 1.0.0 | 2026-01-04 | 1 | Initial Streamlit Dashboard |

---

## Migration Notes

### Upgrading from 1.4.x to 1.5.x

No breaking changes. New files added:
- `analytics_hub_platform/config/kpi_register.yaml`
- `GOVERNANCE.md`
- `CHANGELOG.md`
- `analytics_hub_platform/infrastructure/compliance_checker.py`

### Upgrading from 1.3.x to 1.4.x

No breaking changes. New environment variables (optional):
- `TELEMETRY_ENABLED` - Enable/disable telemetry (default: true)
- `TELEMETRY_BACKEND` - Backend type: none, file, log (default: log)
- `TELEMETRY_FILE` - File path for file backend

### Upgrading from 1.2.x to 1.3.x

No breaking changes. New optional dependencies:
- `reportlab` - For PDF generation
- `kaleido` - For PNG chart export

---

## Contributors

- Ministry of Economy and Planning - IT Division
- Data Analytics Team
- Quality Assurance Team

---

## Links

- [Help](pages/06_Help.py)
- [Operations Runbook](OPS_RUNBOOK.md)
- [Performance Budgets](PERFORMANCE_BUDGETS.md)
- [Data Contract](DATA_CONTRACT.md)
- [Governance](GOVERNANCE.md)
