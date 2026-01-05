"""
Diagnostic Check Script
Verifies all application components and identifies issues
"""

import sys
from pathlib import Path

print("=" * 70)
print("ANALYTICS HUB PLATFORM - DIAGNOSTIC CHECK")
print("=" * 70)

# 1. Python Version
print(f"\n1. Python Version: {sys.version}")

# 2. Critical Imports
print("\n2. Checking Critical Imports...")
critical_imports = [
    "streamlit",
    "pandas",
    "numpy",
    "plotly",
    "sqlalchemy",
    "pydantic",
    "yaml",
]

for module_name in critical_imports:
    try:
        module = __import__(module_name)
        version = getattr(module, "__version__", "unknown")
        print(f"   ✓ {module_name}: {version}")
    except ImportError as e:
        print(f"   ✗ {module_name}: MISSING - {e}")

# 3. Application Modules
print("\n3. Checking Application Modules...")
app_modules = [
    "analytics_hub_platform.infrastructure.settings",
    "analytics_hub_platform.infrastructure.db_init",
    "analytics_hub_platform.infrastructure.repository",
    "analytics_hub_platform.domain.services",
    "analytics_hub_platform.domain.indicators",
    "analytics_hub_platform.ui.theme",
    "analytics_hub_platform.ui.dark_components",
    "analytics_hub_platform.ui.pages.unified_dashboard",
]

for module_name in app_modules:
    try:
        __import__(module_name)
        print(f"   ✓ {module_name}")
    except Exception as e:
        print(f"   ✗ {module_name}: {e}")

# 4. Database Check
print("\n4. Checking Database...")
try:
    from analytics_hub_platform.infrastructure.db_init import get_engine
    from analytics_hub_platform.infrastructure.repository import get_repository

    engine = get_engine()
    print(f"   ✓ Database Engine: {engine.url}")

    repo = get_repository()
    df = repo.get_all_indicators("mep-sa-001")
    print(f"   ✓ Data Records: {len(df)}")
    print(f"   ✓ Columns: {len(df.columns)}")
except Exception as e:
    print(f"   ✗ Database Error: {e}")

# 5. Configuration
print("\n5. Checking Configuration...")
try:
    from analytics_hub_platform.infrastructure.settings import get_settings

    settings = get_settings()
    print(f"   ✓ Environment: {settings.environment}")
    print(f"   ✓ Database URL: {settings.database_url}")
    print(f"   ✓ Log Level: {settings.log_level}")
except Exception as e:
    print(f"   ✗ Configuration Error: {e}")

# 6. KPI Catalog
print("\n6. Checking KPI Catalog...")
try:
    catalog_path = Path(__file__).parent / "analytics_hub_platform" / "config" / "kpi_catalog.yaml"
    if catalog_path.exists():
        import yaml

        with open(catalog_path, encoding="utf-8") as f:
            catalog = yaml.safe_load(f)
        kpis_count = len(catalog.get("kpis", []))
        print(f"   ✓ KPI Catalog Found: {kpis_count} KPIs")
    else:
        print(f"   ✗ KPI Catalog Not Found: {catalog_path}")
except Exception as e:
    print(f"   ✗ KPI Catalog Error: {e}")

# 7. Streamlit API Check
print("\n7. Checking Streamlit API Compatibility...")
try:
    import streamlit as st

    # Check for deprecated/new APIs
    has_page_link = hasattr(st, "page_link")
    has_dataframe = hasattr(st, "dataframe")
    has_plotly_chart = hasattr(st, "plotly_chart")

    print(f"   ✓ st.page_link available: {has_page_link}")
    print(f"   ✓ st.dataframe available: {has_dataframe}")
    print(f"   ✓ st.plotly_chart available: {has_plotly_chart}")

    # Check dataframe width parameter
    import inspect

    df_sig = inspect.signature(st.dataframe)
    df_params = list(df_sig.parameters.keys())
    print(f"   ✓ st.dataframe parameters: {', '.join(df_params[:8])}")

    chart_sig = inspect.signature(st.plotly_chart)
    chart_params = list(chart_sig.parameters.keys())
    print(f"   ✓ st.plotly_chart parameters: {', '.join(chart_params[:8])}")

except Exception as e:
    print(f"   ✗ Streamlit API Check Error: {e}")

# 8. File Structure
print("\n8. Checking File Structure...")
critical_files = [
    "streamlit_app.py",
    "analytics_hub.db",
    "analytics_hub_platform/__init__.py",
    "analytics_hub_platform/config/kpi_catalog.yaml",
    "analytics_hub_platform/ui/pages/unified_dashboard.py",
    "pages/1_📊_Dashboard.py",
]

for file_path in critical_files:
    path = Path(__file__).parent / file_path
    exists = path.exists()
    status = "✓" if exists else "✗"
    print(f"   {status} {file_path}")

print("\n" + "=" * 70)
print("DIAGNOSTIC CHECK COMPLETE")
print("=" * 70)
