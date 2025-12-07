"""
User Preferences Utility
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

User preference management for personalization.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json
from pathlib import Path

import streamlit as st


@dataclass
class DashboardLayout:
    """Dashboard layout preferences."""
    sidebar_collapsed: bool = False
    chart_height: int = 400
    table_rows_per_page: int = 25
    show_data_quality: bool = True
    show_tooltips: bool = True
    compact_mode: bool = False


@dataclass
class ChartPreferences:
    """Chart visualization preferences."""
    default_chart_type: str = "line"  # line, bar, area
    show_data_labels: bool = True
    show_grid: bool = True
    animation_enabled: bool = True
    color_scheme: str = "default"  # default, colorblind, monochrome


@dataclass
class ExportPreferences:
    """Export preferences."""
    default_format: str = "xlsx"  # xlsx, pdf, pptx
    include_charts: bool = True
    include_metadata: bool = True
    date_format: str = "%Y-%m-%d"


@dataclass
class NotificationPreferences:
    """Notification preferences."""
    show_alerts: bool = True
    alert_threshold_warnings: bool = True
    data_refresh_notifications: bool = True


@dataclass
class UserPreferences:
    """Complete user preferences."""
    
    # Identity
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    
    # Language & Locale
    language: str = "en"
    timezone: str = "Asia/Riyadh"
    date_format: str = "%Y-%m-%d"
    number_format: str = "en_US"
    
    # Default filters
    default_year: Optional[int] = None
    default_quarter: Optional[int] = None
    default_region: Optional[str] = None
    
    # Layout
    layout: DashboardLayout = field(default_factory=DashboardLayout)
    
    # Charts
    charts: ChartPreferences = field(default_factory=ChartPreferences)
    
    # Exports
    exports: ExportPreferences = field(default_factory=ExportPreferences)
    
    # Notifications
    notifications: NotificationPreferences = field(default_factory=NotificationPreferences)
    
    # Favorites
    favorite_kpis: List[str] = field(default_factory=list)
    favorite_regions: List[str] = field(default_factory=list)
    
    # Recent
    recent_views: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["updated_at"] = datetime.utcnow().isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserPreferences":
        """Create from dictionary."""
        layout_data = data.pop("layout", {})
        charts_data = data.pop("charts", {})
        exports_data = data.pop("exports", {})
        notifications_data = data.pop("notifications", {})
        
        return cls(
            layout=DashboardLayout(**layout_data) if layout_data else DashboardLayout(),
            charts=ChartPreferences(**charts_data) if charts_data else ChartPreferences(),
            exports=ExportPreferences(**exports_data) if exports_data else ExportPreferences(),
            notifications=NotificationPreferences(**notifications_data) if notifications_data else NotificationPreferences(),
            **{k: v for k, v in data.items() if k in cls.__dataclass_fields__},
        )


# Session state key
PREFERENCES_KEY = "user_preferences"


def get_user_preferences() -> UserPreferences:
    """
    Get current user preferences.
    
    Returns:
        UserPreferences object
    """
    if PREFERENCES_KEY not in st.session_state:
        st.session_state[PREFERENCES_KEY] = UserPreferences(
            created_at=datetime.utcnow().isoformat()
        )
    
    prefs = st.session_state[PREFERENCES_KEY]
    
    # Ensure it's a UserPreferences object
    if isinstance(prefs, dict):
        prefs = UserPreferences.from_dict(prefs)
        st.session_state[PREFERENCES_KEY] = prefs
    
    return prefs


def save_user_preferences(preferences: UserPreferences) -> bool:
    """
    Save user preferences.
    
    Args:
        preferences: UserPreferences object to save
    
    Returns:
        True if successful
    """
    preferences.updated_at = datetime.utcnow().isoformat()
    st.session_state[PREFERENCES_KEY] = preferences
    
    # In production, this would persist to database
    # For now, just update session state
    
    return True


def update_preference(key: str, value: Any) -> bool:
    """
    Update a single preference value.
    
    Args:
        key: Preference key (dot notation for nested)
        value: New value
    
    Returns:
        True if successful
    """
    prefs = get_user_preferences()
    
    parts = key.split(".")
    
    if len(parts) == 1:
        if hasattr(prefs, key):
            setattr(prefs, key, value)
        else:
            return False
    elif len(parts) == 2:
        parent, child = parts
        if hasattr(prefs, parent):
            parent_obj = getattr(prefs, parent)
            if hasattr(parent_obj, child):
                setattr(parent_obj, child, value)
            else:
                return False
        else:
            return False
    else:
        return False
    
    return save_user_preferences(prefs)


def add_to_favorites(kpi_id: str) -> bool:
    """
    Add a KPI to favorites.
    
    Args:
        kpi_id: KPI identifier
    
    Returns:
        True if added
    """
    prefs = get_user_preferences()
    if kpi_id not in prefs.favorite_kpis:
        prefs.favorite_kpis.append(kpi_id)
        return save_user_preferences(prefs)
    return False


def remove_from_favorites(kpi_id: str) -> bool:
    """
    Remove a KPI from favorites.
    
    Args:
        kpi_id: KPI identifier
    
    Returns:
        True if removed
    """
    prefs = get_user_preferences()
    if kpi_id in prefs.favorite_kpis:
        prefs.favorite_kpis.remove(kpi_id)
        return save_user_preferences(prefs)
    return False


def add_recent_view(view_name: str, max_recent: int = 10) -> None:
    """
    Add a view to recent views list.
    
    Args:
        view_name: Name of the view
        max_recent: Maximum recent items to keep
    """
    prefs = get_user_preferences()
    
    # Remove if already exists
    if view_name in prefs.recent_views:
        prefs.recent_views.remove(view_name)
    
    # Add to front
    prefs.recent_views.insert(0, view_name)
    
    # Trim list
    prefs.recent_views = prefs.recent_views[:max_recent]
    
    save_user_preferences(prefs)


def reset_preferences() -> UserPreferences:
    """
    Reset preferences to defaults.
    
    Returns:
        New default UserPreferences
    """
    prefs = UserPreferences(created_at=datetime.utcnow().isoformat())
    st.session_state[PREFERENCES_KEY] = prefs
    return prefs


def export_preferences() -> str:
    """
    Export preferences as JSON.
    
    Returns:
        JSON string
    """
    prefs = get_user_preferences()
    return json.dumps(prefs.to_dict(), indent=2)


def import_preferences(json_str: str) -> bool:
    """
    Import preferences from JSON.
    
    Args:
        json_str: JSON string
    
    Returns:
        True if successful
    """
    try:
        data = json.loads(json_str)
        prefs = UserPreferences.from_dict(data)
        return save_user_preferences(prefs)
    except (json.JSONDecodeError, TypeError, KeyError):
        return False


def get_preference_schema() -> Dict[str, Any]:
    """
    Get preference schema for UI generation.
    
    Returns:
        Schema dictionary
    """
    return {
        "language": {
            "type": "select",
            "options": ["en", "ar"],
            "labels": {"en": "English", "ar": "العربية"},
            "default": "en",
        },
        "layout.compact_mode": {
            "type": "toggle",
            "label": "Compact Mode",
            "default": False,
        },
        "layout.table_rows_per_page": {
            "type": "select",
            "options": [10, 25, 50, 100],
            "label": "Rows per Page",
            "default": 25,
        },
        "charts.show_data_labels": {
            "type": "toggle",
            "label": "Show Data Labels",
            "default": True,
        },
        "charts.animation_enabled": {
            "type": "toggle",
            "label": "Enable Animations",
            "default": True,
        },
        "exports.default_format": {
            "type": "select",
            "options": ["xlsx", "pdf", "pptx"],
            "label": "Default Export Format",
            "default": "xlsx",
        },
        "notifications.show_alerts": {
            "type": "toggle",
            "label": "Show Alerts",
            "default": True,
        },
    }
