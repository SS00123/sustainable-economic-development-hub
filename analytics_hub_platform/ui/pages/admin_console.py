"""
Admin Console Page
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Administration page for KPI management, tenant configuration, and system settings.
"""

from pathlib import Path

import pandas as pd
import streamlit as st
import yaml

from analytics_hub_platform.config.config import get_config
from analytics_hub_platform.config.theme import get_theme
from analytics_hub_platform.infrastructure.security import RBACManager, UserRole
from analytics_hub_platform.infrastructure.settings import get_settings
from analytics_hub_platform.locale import get_strings
from analytics_hub_platform.ui.filters import get_filter_state
from analytics_hub_platform.ui.layout import (
    inject_custom_css,
    render_footer,
    render_header,
    render_section_header,
)


def load_kpi_catalog() -> dict:
    """Load KPI definitions from catalog."""
    catalog_path = Path(__file__).parent.parent.parent / "config" / "kpi_catalog.yaml"
    try:
        with open(catalog_path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return {"kpis": []}


def render_admin_console() -> None:
    """Render the admin console page."""
    inject_custom_css()
    theme = get_theme()

    filters = get_filter_state()
    strings = get_strings(filters.language)

    render_header(
        title=strings.get("admin_title", "Administration Console"),
        subtitle=strings.get("admin_subtitle", "System Configuration and Management"),
        language=filters.language,
    )

    # Role check
    rbac = RBACManager()
    current_role = st.session_state.get("user_role", UserRole.ANALYST)

    # Check permission by role directly (has_permission expects User, but we have role)
    role_permissions = rbac.ROLE_PERMISSIONS.get(current_role, [])
    if "admin_access" not in role_permissions:
        st.warning("⚠️ Admin access required. This is a demo view.")

    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📊 KPI Management",
            "🏢 Tenant Info",
            "👤 User Roles",
            "⚙️ System Settings",
        ]
    )

    with tab1:
        render_kpi_management(theme)

    with tab2:
        render_tenant_info(theme)

    with tab3:
        render_user_roles(theme)

    with tab4:
        render_system_settings(theme)

    # Footer
    render_footer(filters.language)


def render_kpi_management(theme) -> None:
    """Render KPI catalog management section."""
    render_section_header(title="KPI Catalog", icon="📊")

    catalog = load_kpi_catalog()
    kpis = catalog.get("kpis", [])

    if not kpis:
        st.info("No KPIs configured.")
        return

    # Convert to DataFrame for display
    kpi_data = []
    for kpi in kpis:
        kpi_data.append(
            {
                "ID": kpi.get("id", ""),
                "Name (EN)": kpi.get("display_name", {}).get("en", ""),
                "Name (AR)": kpi.get("display_name", {}).get("ar", ""),
                "Unit": kpi.get("unit", ""),
                "Weight": kpi.get("weight", 0),
                "Higher Better": "✓" if kpi.get("higher_is_better", True) else "✗",
            }
        )

    df = pd.DataFrame(kpi_data)

    st.dataframe(
        df,
        width=None,
        hide_index=True,
    )

    # Threshold details
    st.markdown("### Threshold Configuration")

    selected_kpi = st.selectbox(
        "Select KPI to view thresholds:",
        options=[kpi.get("id") for kpi in kpis],
        format_func=lambda x: next(
            (k.get("display_name", {}).get("en", x) for k in kpis if k.get("id") == x), x
        ),
    )

    if selected_kpi:
        kpi_info = next((k for k in kpis if k.get("id") == selected_kpi), None)
        if kpi_info:
            thresholds = kpi_info.get("thresholds", {})

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(
                    f"""
                <div style="background: {theme.colors.status_green}20;
                            border-left: 4px solid {theme.colors.status_green};
                            padding: 15px; border-radius: 8px;">
                    <strong style="color: {theme.colors.status_green};">Green</strong><br/>
                    {thresholds.get("green", "N/A")}
                </div>
                """,
                    unsafe_allow_html=True,
                )

            with col2:
                st.markdown(
                    f"""
                <div style="background: {theme.colors.status_amber}20;
                            border-left: 4px solid {theme.colors.status_amber};
                            padding: 15px; border-radius: 8px;">
                    <strong style="color: {theme.colors.status_amber};">Amber</strong><br/>
                    {thresholds.get("amber", "N/A")}
                </div>
                """,
                    unsafe_allow_html=True,
                )

            with col3:
                st.markdown(
                    f"""
                <div style="background: {theme.colors.status_red}20;
                            border-left: 4px solid {theme.colors.status_red};
                            padding: 15px; border-radius: 8px;">
                    <strong style="color: {theme.colors.status_red};">Red</strong><br/>
                    {thresholds.get("red", "N/A")}
                </div>
                """,
                    unsafe_allow_html=True,
                )

            st.markdown(f"""
            **Formula:** `{kpi_info.get("formula", "N/A")}`
            """)


def render_tenant_info(theme) -> None:
    """Render tenant information section."""
    render_section_header(title="Tenant Configuration", icon="🏢")

    settings = get_settings()

    st.markdown(
        f"""
    <div style="background: {theme.colors.surface};
                border: 1px solid {theme.colors.border};
                border-radius: 12px; padding: 24px;">
        <h4 style="color: {theme.colors.primary}; margin-bottom: 20px;">Current Tenant</h4>
        <table style="width: 100%;">
            <tr>
                <td style="padding: 8px 0; color: {theme.colors.text_muted};">Tenant ID</td>
                <td style="padding: 8px 0; font-weight: 600;">{settings.default_tenant_id}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: {theme.colors.text_muted};">Environment</td>
                <td style="padding: 8px 0; font-weight: 600;">{settings.environment}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: {theme.colors.text_muted};">Database</td>
                <td style="padding: 8px 0; font-weight: 600;">{settings.db_path or "Default SQLite"}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: {theme.colors.text_muted};">Debug Mode</td>
                <td style="padding: 8px 0; font-weight: 600;">{"Enabled" if settings.debug else "Disabled"}</td>
            </tr>
        </table>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.info(
        "💡 Multi-tenant support ready. Production deployment will connect to organization directory."
    )


def render_user_roles(theme) -> None:
    """Render user roles and permissions section."""
    render_section_header(title="Role-Based Access Control", icon="👤")

    roles_data = [
        {
            "Role": "Minister",
            "Level": "Executive",
            "Dashboard Access": "✓",
            "Export": "✓",
            "Admin": "✗",
            "Description": "High-level KPI overview and strategic insights",
        },
        {
            "Role": "Executive",
            "Level": "Senior",
            "Dashboard Access": "✓",
            "Export": "✓",
            "Admin": "✗",
            "Description": "Executive dashboards with trend analysis",
        },
        {
            "Role": "Director",
            "Level": "Management",
            "Dashboard Access": "✓",
            "Export": "✓",
            "Admin": "✗",
            "Description": "Detailed analytics and regional comparisons",
        },
        {
            "Role": "Analyst",
            "Level": "Operational",
            "Dashboard Access": "✓",
            "Export": "✓",
            "Admin": "✗",
            "Description": "Full data access and analysis tools",
        },
        {
            "Role": "Admin",
            "Level": "System",
            "Dashboard Access": "✓",
            "Export": "✓",
            "Admin": "✓",
            "Description": "System configuration and user management",
        },
    ]

    df = pd.DataFrame(roles_data)

    st.dataframe(df, width=None, hide_index=True)

    # Current session role selector (demo)
    st.markdown("### Demo Role Selector")

    selected_role = st.selectbox(
        "Switch Role (Demo Mode):",
        options=["ANALYST", "DIRECTOR", "EXECUTIVE", "MINISTER", "ADMIN"],
        index=0,
    )

    if st.button("Apply Role"):
        st.session_state["user_role"] = UserRole[selected_role]
        st.success(f"Role switched to {selected_role}")
        st.rerun()


def render_system_settings(theme) -> None:
    """Render system settings section."""
    render_section_header(title="System Configuration", icon="⚙️")

    config = get_config()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Application Settings")

        st.markdown(f"""
        | Setting | Value |
        |---------|-------|
        | Default Year | {config.default_year} |
        | Default Quarter | {config.default_quarter} |
        | Max Export Rows | 10,000 |
        | Cache TTL | {config.cache_ttl_seconds}s |
        | Pagination | 50 items |
        """)

    with col2:
        st.markdown("### Feature Flags")

        st.markdown("""
        | Feature | Status |
        |---------|--------|
        | Multi-tenant | ✓ Ready |
        | SSO Integration | ⏳ Stub |
        | Export PDF | ✓ Active |
        | Export PPT | ✓ Active |
        | Export Excel | ✓ Active |
        | Arabic Support | ✓ Active |
        """)

    st.markdown("---")

    st.markdown("### Database Operations")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 Refresh Cache", use_container_width=False):
            st.cache_data.clear()
            st.success("Cache cleared!")

    with col2:
        if st.button("📊 Regenerate Data", use_container_width=False):
            st.info("Data regeneration available in development mode.")

    with col3:
        if st.button("📋 Export Logs", use_container_width=False):
            st.info("Log export functionality.")
