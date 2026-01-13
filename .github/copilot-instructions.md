# Copilot Instructions — Analytics Hub Platform

## Architecture Overview

This is a **Streamlit multi-page analytics platform** for Saudi Arabia's Ministry of Economy and Planning. The codebase follows a layered architecture:

```
streamlit_app.py              → Entry point (run with: streamlit run streamlit_app.py)
pages/01_Dashboard.py...      → Streamlit multi-page routes
analytics_hub_platform/
├── domain/                   → Business logic, models, calculations (Pydantic models)
├── infrastructure/           → Database, auth, caching, repository pattern
├── config/                   → Settings, KPI definitions (YAML-driven)
└── ui/                       → Streamlit components, themes, HTML rendering
```

**Data Flow:** `Repository` → `domain/services.py` → `ui/` components → Streamlit pages.  
All queries are **tenant-aware** (`tenant_id` parameter). Default tenant: `ministry_economy`.

## Critical Patterns

### KPI Configuration
KPIs are defined in `config/kpi_catalog.yaml`, not code. Add new KPIs there with thresholds, weights, and translations:
```yaml
- id: my_new_kpi
  display_name_en: "My KPI"
  display_name_ar: "المؤشر"
  higher_is_better: true
  thresholds: { green: 70, amber: 40 }
```

### Domain Models (Pydantic)
All models in `domain/models.py` use Pydantic v2. Key models: `FilterParams`, `KPIThresholds`, `UserRole`, `KPIStatus`. Always use `model_config = ConfigDict(from_attributes=True)` for ORM compatibility.

### HTML Rendering
Never use `st.markdown(unsafe_allow_html=True)` directly. Use `ui/html.py`:
```python
from analytics_hub_platform.ui.html import render_html
render_html("<div>...</div>")  # Handles Streamlit version compatibility
```

### Database Pattern
- SQLite for PoC, designed for PostgreSQL migration
- Use `Repository` class from `infrastructure/repository.py` for all data access
- Synthetic data generation in `db_init.py` — call `initialize_database()` once per session
- Schema defined in `alembic/versions/` for migrations

### Session State Initialization
Every Streamlit page must call at top:
```python
from analytics_hub_platform.ui.ui_components import initialize_page_session_state
initialize_page_session_state()
```

## Developer Commands

```powershell
# Run app locally
streamlit run streamlit_app.py

# Run tests (use fixtures from conftest.py)
pytest tests/ -v

# Lint and format
ruff check . --fix
ruff format .

# Type checking
mypy analytics_hub_platform/

# Database migrations
alembic upgrade head
```

## Testing Conventions

- Tests in `tests/` use **pytest** with fixtures in `conftest.py`
- Extend existing fixtures (`sample_filter_params`, `sample_dataframe`) rather than duplicating setup
- Tests must be deterministic — seed randomness with `np.random.seed(42)`
- Use `pytest.approx()` for float comparisons

## Code Style

- **Line length:** 100 chars (configured in `ruff.toml`)
- **Python target:** 3.11+
- **Type hints:** Required for public functions
- **Imports:** Sort with `ruff` — first-party package is `analytics_hub_platform`
- Follow existing patterns in the file you're editing

## Key Extension Points

| To add... | Edit... |
|-----------|---------|
| New KPI | `config/kpi_catalog.yaml` |
| New page | `pages/XX_Name.py` (numbered for ordering) |
| New domain logic | `domain/` (pure functions in `indicators.py`, services in `services.py`) |
| New UI component | `ui/components/` or `ui/ui_components.py` |
| Database column | `infrastructure/db_init.py` + new Alembic migration |

## Don't

- Don't add new dependencies without updating `pyproject.toml` and `requirements.txt`
- Don't create new config patterns — use existing `config/config.py` dataclasses
- Don't bypass Repository for database access
- Don't use `st.html()` directly — use `render_html()` wrapper
