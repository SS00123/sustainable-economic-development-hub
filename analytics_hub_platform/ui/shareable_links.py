"""
Shareable Links Module
Sustainable Economic Development Analytics Hub

Provides functionality for:
- Generating shareable URLs with query parameters
- Parsing URL parameters to restore view state
- Managing presets/saved views
"""

import base64
import hashlib
import json
import urllib.parse
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

import streamlit as st


# =============================================================================
# VIEW STATE MODEL
# =============================================================================


@dataclass
class ViewState:
    """Represents the current dashboard view state."""

    # Filter parameters
    year: int | None = None
    quarter: int | None = None
    region: str | None = None
    tenant_id: str = "ministry_economy"

    # View settings
    language: str = "en"
    pillar: str | None = None  # economic, social, environmental
    chart_type: str | None = None

    # Comparison settings
    compare_period: bool = False
    compare_region: bool = False

    # Page-specific
    page: str = "dashboard"

    def to_query_params(self) -> dict[str, str]:
        """Convert state to URL query parameters."""
        params = {}

        if self.year:
            params["year"] = str(self.year)
        if self.quarter:
            params["q"] = str(self.quarter)
        if self.region:
            params["region"] = self.region
        if self.tenant_id != "ministry_economy":
            params["tenant"] = self.tenant_id
        if self.language != "en":
            params["lang"] = self.language
        if self.pillar:
            params["pillar"] = self.pillar
        if self.chart_type:
            params["chart"] = self.chart_type
        if self.compare_period:
            params["cmp_period"] = "1"
        if self.compare_region:
            params["cmp_region"] = "1"
        if self.page != "dashboard":
            params["page"] = self.page

        return params

    @classmethod
    def from_query_params(cls, params: dict[str, str]) -> "ViewState":
        """Create ViewState from URL query parameters."""
        return cls(
            year=int(params["year"]) if "year" in params else None,
            quarter=int(params["q"]) if "q" in params else None,
            region=params.get("region"),
            tenant_id=params.get("tenant", "ministry_economy"),
            language=params.get("lang", "en"),
            pillar=params.get("pillar"),
            chart_type=params.get("chart"),
            compare_period=params.get("cmp_period") == "1",
            compare_region=params.get("cmp_region") == "1",
            page=params.get("page", "dashboard"),
        )

    def to_encoded_state(self) -> str:
        """Encode state as a compact base64 string."""
        state_dict = {k: v for k, v in asdict(self).items() if v is not None and v != ""}
        json_str = json.dumps(state_dict, separators=(",", ":"))
        return base64.urlsafe_b64encode(json_str.encode()).decode()

    @classmethod
    def from_encoded_state(cls, encoded: str) -> "ViewState":
        """Decode state from a base64 string."""
        try:
            json_str = base64.urlsafe_b64decode(encoded.encode()).decode()
            state_dict = json.loads(json_str)
            return cls(**state_dict)
        except Exception:
            return cls()


# =============================================================================
# URL GENERATION
# =============================================================================


def generate_share_url(state: ViewState, base_url: str | None = None) -> str:
    """
    Generate a shareable URL for the current view state.

    Args:
        state: Current view state
        base_url: Base URL (defaults to Streamlit app URL)

    Returns:
        Complete shareable URL
    """
    if base_url is None:
        # Try to get from Streamlit config
        try:
            base_url = st.get_option("browser.serverAddress") or "http://localhost:8501"
        except Exception:
            base_url = "http://localhost:8501"

    params = state.to_query_params()
    query_string = urllib.parse.urlencode(params)

    if query_string:
        return f"{base_url}?{query_string}"
    return base_url


def generate_compact_share_url(state: ViewState, base_url: str | None = None) -> str:
    """
    Generate a compact shareable URL using encoded state.

    Args:
        state: Current view state
        base_url: Base URL

    Returns:
        Compact shareable URL
    """
    if base_url is None:
        base_url = "http://localhost:8501"

    encoded = state.to_encoded_state()
    return f"{base_url}?s={encoded}"


def parse_url_params() -> ViewState:
    """
    Parse current URL query parameters into ViewState.

    Returns:
        ViewState from URL params
    """
    params = st.query_params

    # Check for compact encoded state first
    if "s" in params:
        return ViewState.from_encoded_state(params["s"])

    # Parse individual parameters
    return ViewState.from_query_params(dict(params))


def apply_url_params_to_session():
    """
    Apply URL parameters to session state.
    Call this at the start of each page to sync URL with session.
    """
    state = parse_url_params()

    if state.year:
        st.session_state["selected_year"] = state.year
    if state.quarter:
        st.session_state["selected_quarter"] = state.quarter
    if state.region:
        st.session_state["selected_region"] = state.region
    if state.language:
        st.session_state["language"] = state.language
    if state.pillar:
        st.session_state["active_pillar"] = state.pillar


# =============================================================================
# SAVED VIEWS / PRESETS
# =============================================================================


@dataclass
class SavedView:
    """A saved view/preset configuration."""

    id: str
    name: str
    description: str
    state: ViewState
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = "system"
    is_default: bool = False
    is_public: bool = True


# Default presets
DEFAULT_PRESETS: list[SavedView] = [
    SavedView(
        id="exec_summary",
        name="Executive Summary",
        description="High-level KPIs for leadership briefing",
        state=ViewState(page="dashboard", pillar=None),
        is_default=True,
    ),
    SavedView(
        id="economic_deep_dive",
        name="Economic Deep Dive",
        description="Detailed economic indicators with trends",
        state=ViewState(page="kpis", pillar="economic", compare_period=True),
    ),
    SavedView(
        id="regional_comparison",
        name="Regional Comparison",
        description="Compare all regions side by side",
        state=ViewState(page="data", compare_region=True),
    ),
    SavedView(
        id="sustainability_trends",
        name="Sustainability Trends",
        description="Environmental and sustainability metrics over time",
        state=ViewState(page="trends", pillar="environmental"),
    ),
    SavedView(
        id="arabic_view",
        name="العرض العربي",
        description="Dashboard in Arabic with RTL layout",
        state=ViewState(language="ar"),
    ),
]


class PresetManager:
    """Manager for saved views and presets."""

    SESSION_KEY = "saved_presets"

    def __init__(self):
        """Initialize preset manager with defaults."""
        if self.SESSION_KEY not in st.session_state:
            st.session_state[self.SESSION_KEY] = {p.id: p for p in DEFAULT_PRESETS}

    @property
    def presets(self) -> dict[str, SavedView]:
        """Get all saved presets."""
        return st.session_state.get(self.SESSION_KEY, {})

    def get_preset(self, preset_id: str) -> SavedView | None:
        """Get a specific preset by ID."""
        return self.presets.get(preset_id)

    def save_preset(self, preset: SavedView) -> bool:
        """Save a new or updated preset."""
        if self.SESSION_KEY not in st.session_state:
            st.session_state[self.SESSION_KEY] = {}
        st.session_state[self.SESSION_KEY][preset.id] = preset
        return True

    def delete_preset(self, preset_id: str) -> bool:
        """Delete a preset."""
        if preset_id in st.session_state.get(self.SESSION_KEY, {}):
            del st.session_state[self.SESSION_KEY][preset_id]
            return True
        return False

    def create_preset_from_current(
        self,
        name: str,
        description: str = "",
        is_public: bool = True,
    ) -> SavedView:
        """Create a preset from current session state."""
        state = ViewState(
            year=st.session_state.get("selected_year"),
            quarter=st.session_state.get("selected_quarter"),
            region=st.session_state.get("selected_region"),
            language=st.session_state.get("language", "en"),
            pillar=st.session_state.get("active_pillar"),
        )

        preset_id = hashlib.md5(f"{name}{datetime.now().isoformat()}".encode()).hexdigest()[:8]

        preset = SavedView(
            id=preset_id,
            name=name,
            description=description,
            state=state,
            is_public=is_public,
        )

        self.save_preset(preset)
        return preset

    def apply_preset(self, preset_id: str) -> bool:
        """Apply a preset to the current session."""
        preset = self.get_preset(preset_id)
        if not preset:
            return False

        state = preset.state

        if state.year:
            st.session_state["selected_year"] = state.year
        if state.quarter:
            st.session_state["selected_quarter"] = state.quarter
        if state.region:
            st.session_state["selected_region"] = state.region
        if state.language:
            st.session_state["language"] = state.language
        if state.pillar:
            st.session_state["active_pillar"] = state.pillar

        # Update URL
        st.query_params.update(state.to_query_params())

        return True


# =============================================================================
# UI COMPONENTS
# =============================================================================


def render_share_button():
    """Render a share button that copies the current URL."""
    state = ViewState(
        year=st.session_state.get("selected_year"),
        quarter=st.session_state.get("selected_quarter"),
        region=st.session_state.get("selected_region"),
        language=st.session_state.get("language", "en"),
        pillar=st.session_state.get("active_pillar"),
    )

    url = generate_share_url(state)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.text_input("Share URL", value=url, key="share_url_display", disabled=True)
    with col2:
        st.markdown(
            f"""
            <a href="{url}" target="_blank" style="
                display: inline-block;
                padding: 0.5rem 1rem;
                background-color: #1E40AF;
                color: white;
                border-radius: 0.25rem;
                text-decoration: none;
                margin-top: 1.5rem;
            ">🔗 Copy Link</a>
            """,
            unsafe_allow_html=True,
        )


def render_preset_selector():
    """Render a dropdown to select and apply presets."""
    manager = PresetManager()

    preset_options = {p.name: p.id for p in manager.presets.values()}

    if not preset_options:
        st.info("No saved views available")
        return

    selected_name = st.selectbox(
        "📁 Load Saved View",
        options=["Select a view..."] + list(preset_options.keys()),
        key="preset_selector",
    )

    if selected_name and selected_name != "Select a view...":
        preset_id = preset_options[selected_name]
        preset = manager.get_preset(preset_id)

        if preset:
            st.caption(preset.description)

            if st.button("Apply View", key="apply_preset_btn"):
                manager.apply_preset(preset_id)
                st.success(f"Applied: {preset.name}")
                st.rerun()


def render_save_view_dialog():
    """Render a dialog to save the current view."""
    with st.expander("💾 Save Current View"):
        name = st.text_input("View Name", key="new_preset_name")
        description = st.text_area("Description (optional)", key="new_preset_desc")
        is_public = st.checkbox("Make public", value=True, key="new_preset_public")

        if st.button("Save View", key="save_preset_btn"):
            if name:
                manager = PresetManager()
                preset = manager.create_preset_from_current(name, description, is_public)
                st.success(f"Saved: {preset.name}")
            else:
                st.error("Please enter a name")
