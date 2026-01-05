# Architecture Map

## Entry Points
- **Primary:** `streamlit_app.py` (Multi-page application entry point)
- **Legacy/Prototype:** `app.py` (Single-file dashboard, 1779 lines)

## Module Structure
- **`analytics_hub_platform/`**: Core package
    - **`api/`**: FastAPI routers (likely for a separate API service, not used by Streamlit directly?)
    - **`config/`**: Configuration management (`config.py`, `kpi_catalog.yaml`)
    - **`domain/`**: Business logic and models (`models.py`, `services.py`)
    - **`infrastructure/`**: Database and logging
    - **`ui/`**: UI components and themes
    - **`utils/`**: Utility functions
- **`data/`**: Data generation and import tools
- **`ml/`**: Machine learning models
- **`pages/`**: Streamlit pages (01-09)
- **`scripts/`**: Utility scripts

## Data Flow
1.  **Ingestion:** `data/excel_importer.py` -> SQLite DB
2.  **Storage:** SQLite (`analytics_hub.db`) managed via SQLAlchemy/Alembic
3.  **Processing:** `domain/` services process data
4.  **Presentation:** Streamlit pages render data using `ui/` components

## Key Dependencies
- Streamlit
- Pandas, NumPy
- Plotly
- SQLAlchemy, Alembic
- Pydantic
