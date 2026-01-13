# Configuration

## Environment
- Python 3.11+

## Config Files
- `analytics_hub_platform/config/config.py` — app settings
- `analytics_hub_platform/config/kpi_catalog.yaml` — KPI definitions
- `requirements.txt` / `requirements-dev.txt`

## Dev Setup
```powershell
cd V:\POC\analytics_hub_platform
pip install -r requirements-dev.txt
pytest -q
```

