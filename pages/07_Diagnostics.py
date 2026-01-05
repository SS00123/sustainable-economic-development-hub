"""
Diagnostics Page
Sustainable Economic Development Analytics Hub

Production smoke-check panel showing:
- Application version and environment
- Database health and connection status
- Cache statistics
- System resource signals
- Last data refresh timestamp
- Correlation ID for request tracing
"""

import os
import platform
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

# Generate correlation ID for this session/request
if "correlation_id" not in st.session_state:
    st.session_state.correlation_id = str(uuid.uuid4())[:8]


def get_app_version() -> str:
    """Get application version from pyproject.toml or environment."""
    version = os.getenv("APP_VERSION", None)
    if version:
        return version
    
    # Try to read from pyproject.toml
    try:
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        if pyproject_path.exists():
            content = pyproject_path.read_text()
            for line in content.split("\n"):
                if line.strip().startswith("version"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    except Exception:
        pass
    
    return "1.0.0-dev"


def get_environment() -> str:
    """Determine current environment."""
    env = os.getenv("ANALYTICS_HUB_ENV", os.getenv("STREAMLIT_ENV", "development"))
    return env.lower()


def check_database_health() -> dict:
    """Check database connectivity and basic health."""
    from analytics_hub_platform.infrastructure.db_init import get_engine
    
    result = {
        "status": "unknown",
        "message": "",
        "connection_pool": {},
        "table_counts": {},
    }
    
    try:
        engine = get_engine()
        
        # Test connection
        with engine.connect() as conn:
            # Simple query to verify connectivity
            conn.execute(__import__("sqlalchemy").text("SELECT 1"))
            result["status"] = "healthy"
            result["message"] = "Database connection successful"
            
            # Get table counts
            for table in ["sustainability_indicators", "tenants", "users"]:
                try:
                    count_result = conn.execute(
                        __import__("sqlalchemy").text(f"SELECT COUNT(*) FROM {table}")
                    )
                    result["table_counts"][table] = count_result.scalar()
                except Exception:
                    result["table_counts"][table] = "N/A"
            
            # Connection pool stats (if available)
            pool = engine.pool
            if hasattr(pool, "size"):
                result["connection_pool"]["size"] = pool.size()
            if hasattr(pool, "checkedin"):
                result["connection_pool"]["available"] = pool.checkedin()
            if hasattr(pool, "checkedout"):
                result["connection_pool"]["in_use"] = pool.checkedout()
                
    except Exception as e:
        result["status"] = "unhealthy"
        result["message"] = str(e)
    
    return result


def get_cache_stats() -> dict:
    """Get Streamlit cache statistics."""
    stats = {
        "session_state_keys": len(st.session_state),
        "cache_data_info": [],
        "cache_resource_info": [],
    }
    
    # List session state keys (sanitized)
    stats["session_state_sample"] = list(st.session_state.keys())[:10]
    
    # Check for timing data
    if "section_timings" in st.session_state:
        stats["section_timings"] = st.session_state.section_timings
    
    return stats


def get_system_resources() -> dict:
    """Get basic system resource information."""
    import shutil
    
    resources = {
        "python_version": sys.version.split()[0],
        "platform": platform.system(),
        "platform_version": platform.version()[:50],
        "architecture": platform.machine(),
    }
    
    # Disk space
    try:
        disk = shutil.disk_usage("/")
        resources["disk_total_gb"] = round(disk.total / (1024**3), 1)
        resources["disk_free_gb"] = round(disk.free / (1024**3), 1)
        resources["disk_used_percent"] = round((disk.used / disk.total) * 100, 1)
    except Exception:
        pass
    
    # Memory (if psutil available)
    try:
        import psutil
        mem = psutil.virtual_memory()
        resources["memory_total_gb"] = round(mem.total / (1024**3), 1)
        resources["memory_available_gb"] = round(mem.available / (1024**3), 1)
        resources["memory_used_percent"] = mem.percent
        resources["cpu_percent"] = psutil.cpu_percent(interval=0.1)
    except ImportError:
        resources["memory_note"] = "psutil not installed"
    except Exception:
        pass
    
    return resources


def get_last_data_refresh() -> dict:
    """Get timestamp of last data load."""
    from analytics_hub_platform.infrastructure.db_init import get_engine
    
    result = {
        "last_load_timestamp": None,
        "last_batch_id": None,
    }
    
    try:
        engine = get_engine()
        with engine.connect() as conn:
            query = __import__("sqlalchemy").text("""
                SELECT MAX(load_timestamp) as last_load, load_batch_id
                FROM sustainability_indicators
                GROUP BY load_batch_id
                ORDER BY MAX(load_timestamp) DESC
                LIMIT 1
            """)
            row = conn.execute(query).fetchone()
            if row:
                result["last_load_timestamp"] = row[0]
                result["last_batch_id"] = row[1]
    except Exception as e:
        result["error"] = str(e)
    
    return result


def render_diagnostics_page():
    """Render the diagnostics page."""
    st.set_page_config(
        page_title="Diagnostics | Analytics Hub",
        page_icon="🔧",
        layout="wide",
    )
    
    correlation_id = st.session_state.correlation_id
    
    st.title("🔧 System Diagnostics")
    st.caption(f"Correlation ID: `{correlation_id}` | Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    # Version and Environment
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Version", get_app_version())
    with col2:
        env = get_environment()
        env_color = "🟢" if env == "production" else "🟡" if env == "staging" else "🔵"
        st.metric("Environment", f"{env_color} {env.title()}")
    with col3:
        st.metric("Correlation ID", correlation_id)
    
    st.divider()
    
    # Database Health
    st.subheader("💾 Database Health")
    
    with st.spinner("Checking database..."):
        db_health = check_database_health()
    
    status_icon = "✅" if db_health["status"] == "healthy" else "❌"
    st.write(f"**Status:** {status_icon} {db_health['status'].title()}")
    st.write(f"**Message:** {db_health['message']}")
    
    if db_health["table_counts"]:
        st.write("**Table Counts:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Indicators", db_health["table_counts"].get("sustainability_indicators", "N/A"))
        with col2:
            st.metric("Tenants", db_health["table_counts"].get("tenants", "N/A"))
        with col3:
            st.metric("Users", db_health["table_counts"].get("users", "N/A"))
    
    if db_health["connection_pool"]:
        with st.expander("Connection Pool Details"):
            st.json(db_health["connection_pool"])
    
    st.divider()
    
    # Last Data Refresh
    st.subheader("🔄 Data Refresh Status")
    refresh_info = get_last_data_refresh()
    
    if refresh_info.get("last_load_timestamp"):
        st.write(f"**Last Load:** {refresh_info['last_load_timestamp']}")
        st.write(f"**Batch ID:** `{refresh_info.get('last_batch_id', 'N/A')}`")
    else:
        st.warning("No data load timestamps found")
    
    st.divider()
    
    # Cache Statistics
    st.subheader("📊 Cache Statistics")
    cache_stats = get_cache_stats()
    
    st.metric("Session State Keys", cache_stats["session_state_keys"])
    
    if cache_stats.get("section_timings"):
        st.write("**Section Render Times:**")
        for section, timing in cache_stats["section_timings"].items():
            st.write(f"  - {section}: {timing:.2f}ms")
    
    with st.expander("Session State Keys (Sample)"):
        st.json(cache_stats.get("session_state_sample", []))
    
    st.divider()
    
    # System Resources
    st.subheader("💻 System Resources")
    resources = get_system_resources()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Python:** {resources.get('python_version', 'N/A')}")
        st.write(f"**Platform:** {resources.get('platform', 'N/A')} ({resources.get('architecture', 'N/A')})")
        
        if "disk_used_percent" in resources:
            st.progress(resources["disk_used_percent"] / 100, f"Disk: {resources['disk_used_percent']}% used")
    
    with col2:
        if "memory_used_percent" in resources:
            st.write(f"**Memory:** {resources['memory_available_gb']}GB available / {resources['memory_total_gb']}GB total")
            st.progress(resources["memory_used_percent"] / 100, f"Memory: {resources['memory_used_percent']}% used")
            st.write(f"**CPU:** {resources.get('cpu_percent', 'N/A')}%")
        elif "memory_note" in resources:
            st.info(resources["memory_note"])
    
    st.divider()
    
    # Quick Health Checks
    st.subheader("✅ Production Smoke Checklist")
    
    checks = []
    
    # Check 1: Database connectivity
    checks.append(("Database Connection", db_health["status"] == "healthy"))
    
    # Check 2: Has data
    indicator_count = db_health["table_counts"].get("sustainability_indicators", 0)
    checks.append(("Data Available", isinstance(indicator_count, int) and indicator_count > 0))
    
    # Check 3: Environment configured
    checks.append(("Environment Set", get_environment() != ""))
    
    # Check 4: Version defined
    checks.append(("Version Defined", get_app_version() != ""))
    
    # Check 5: Disk space OK
    disk_ok = resources.get("disk_used_percent", 0) < 90
    checks.append(("Disk Space OK (<90%)", disk_ok))
    
    # Display checks
    all_passed = True
    for check_name, passed in checks:
        icon = "✅" if passed else "❌"
        st.write(f"{icon} {check_name}")
        if not passed:
            all_passed = False
    
    st.divider()
    
    if all_passed:
        st.success("🎉 All smoke checks passed! System is ready.")
    else:
        st.error("⚠️ Some checks failed. Review issues above.")
    
    # Export diagnostics button
    if st.button("📋 Copy Diagnostics Report"):
        report = f"""
Analytics Hub Diagnostics Report
================================
Correlation ID: {correlation_id}
Generated: {datetime.now(timezone.utc).isoformat()}
Version: {get_app_version()}
Environment: {get_environment()}

Database:
- Status: {db_health['status']}
- Tables: {db_health['table_counts']}

Resources:
- Python: {resources.get('python_version')}
- Platform: {resources.get('platform')}
- Disk Used: {resources.get('disk_used_percent', 'N/A')}%
- Memory Used: {resources.get('memory_used_percent', 'N/A')}%

Smoke Checks:
{chr(10).join([f"- {name}: {'PASS' if passed else 'FAIL'}" for name, passed in checks])}
        """
        st.code(report)


if __name__ == "__main__":
    render_diagnostics_page()
else:
    render_diagnostics_page()
