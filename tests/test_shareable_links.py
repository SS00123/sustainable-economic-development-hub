"""
Tests for Shareable Links and Presets Module
Sustainable Economic Development Analytics Hub

Tests:
- ViewState creation and serialization
- URL generation and parsing
- Preset management
"""

import base64

from analytics_hub_platform.ui.shareable_links import (
    ViewState,
    SavedView,
    generate_share_url,
    generate_compact_share_url,
    DEFAULT_PRESETS,
)


# =============================================================================
# VIEW STATE TESTS
# =============================================================================


class TestViewState:
    """Tests for ViewState dataclass."""

    def test_default_state(self):
        """Test default ViewState values."""
        state = ViewState()

        assert state.year is None
        assert state.quarter is None
        assert state.region is None
        assert state.tenant_id == "ministry_economy"
        assert state.language == "en"
        assert state.page == "dashboard"

    def test_state_with_values(self):
        """Test ViewState with custom values."""
        state = ViewState(
            year=2024,
            quarter=2,
            region="Riyadh",
            language="ar",
            pillar="economic",
        )

        assert state.year == 2024
        assert state.quarter == 2
        assert state.region == "Riyadh"
        assert state.language == "ar"
        assert state.pillar == "economic"

    def test_to_query_params_basic(self):
        """Test converting state to query parameters."""
        state = ViewState(year=2024, quarter=1, region="Riyadh")
        params = state.to_query_params()

        assert params["year"] == "2024"
        assert params["q"] == "1"
        assert params["region"] == "Riyadh"

    def test_to_query_params_skips_defaults(self):
        """Test that default values are not included in query params."""
        state = ViewState()
        params = state.to_query_params()

        assert "tenant" not in params  # Default tenant
        assert "lang" not in params    # Default language
        assert "page" not in params    # Default page

    def test_to_query_params_includes_non_defaults(self):
        """Test that non-default values are included."""
        state = ViewState(
            language="ar",
            tenant_id="custom_tenant",
            compare_period=True,
        )
        params = state.to_query_params()

        assert params["lang"] == "ar"
        assert params["tenant"] == "custom_tenant"
        assert params["cmp_period"] == "1"

    def test_from_query_params(self):
        """Test creating state from query parameters."""
        params = {
            "year": "2024",
            "q": "3",
            "region": "Eastern",
            "lang": "ar",
        }
        state = ViewState.from_query_params(params)

        assert state.year == 2024
        assert state.quarter == 3
        assert state.region == "Eastern"
        assert state.language == "ar"

    def test_roundtrip_query_params(self):
        """Test state survives roundtrip through query params."""
        original = ViewState(
            year=2024,
            quarter=2,
            region="Makkah",
            language="ar",
            pillar="social",
            compare_period=True,
        )

        params = original.to_query_params()
        restored = ViewState.from_query_params(params)

        assert restored.year == original.year
        assert restored.quarter == original.quarter
        assert restored.region == original.region
        assert restored.language == original.language
        assert restored.pillar == original.pillar
        assert restored.compare_period == original.compare_period


class TestViewStateEncoding:
    """Tests for base64 encoded state."""

    def test_to_encoded_state(self):
        """Test encoding state to base64."""
        state = ViewState(year=2024, quarter=1)
        encoded = state.to_encoded_state()

        assert encoded is not None
        assert len(encoded) > 0
        # Should be valid base64
        decoded = base64.urlsafe_b64decode(encoded.encode())
        assert decoded is not None

    def test_from_encoded_state(self):
        """Test decoding state from base64."""
        state = ViewState(year=2024, quarter=2, region="Riyadh")
        encoded = state.to_encoded_state()
        restored = ViewState.from_encoded_state(encoded)

        assert restored.year == 2024
        assert restored.quarter == 2
        assert restored.region == "Riyadh"

    def test_invalid_encoded_state_returns_default(self):
        """Test that invalid encoded state returns default ViewState."""
        restored = ViewState.from_encoded_state("invalid_base64_data!")

        # Should return default state, not crash
        assert restored.tenant_id == "ministry_economy"


# =============================================================================
# URL GENERATION TESTS
# =============================================================================


class TestURLGeneration:
    """Tests for URL generation functions."""

    def test_generate_share_url_basic(self):
        """Test basic URL generation."""
        state = ViewState(year=2024, quarter=1)
        url = generate_share_url(state, "https://example.com")

        assert "https://example.com" in url
        assert "year=2024" in url
        assert "q=1" in url

    def test_generate_share_url_empty_state(self):
        """Test URL generation with empty state."""
        state = ViewState()
        url = generate_share_url(state, "https://example.com")

        assert url == "https://example.com"

    def test_generate_compact_url(self):
        """Test compact URL generation."""
        state = ViewState(year=2024, region="Riyadh")
        url = generate_compact_share_url(state, "https://example.com")

        assert "https://example.com" in url
        assert "s=" in url  # Compact parameter


# =============================================================================
# SAVED VIEW / PRESET TESTS
# =============================================================================


class TestSavedView:
    """Tests for SavedView dataclass."""

    def test_create_saved_view(self):
        """Test creating a saved view."""
        view = SavedView(
            id="test_view",
            name="Test View",
            description="A test view",
            state=ViewState(year=2024),
        )

        assert view.id == "test_view"
        assert view.name == "Test View"
        assert view.state.year == 2024
        assert view.is_default is False
        assert view.is_public is True

    def test_saved_view_created_at_auto(self):
        """Test that created_at is automatically set."""
        view = SavedView(
            id="test",
            name="Test",
            description="",
            state=ViewState(),
        )

        assert view.created_at is not None


class TestDefaultPresets:
    """Tests for default preset configuration."""

    def test_default_presets_exist(self):
        """Test that default presets are defined."""
        assert len(DEFAULT_PRESETS) > 0

    def test_default_presets_have_required_fields(self):
        """Test that all default presets have required fields."""
        for preset in DEFAULT_PRESETS:
            assert preset.id is not None and preset.id != ""
            assert preset.name is not None and preset.name != ""
            assert preset.state is not None

    def test_executive_summary_preset_exists(self):
        """Test that executive summary preset exists."""
        exec_preset = next(
            (p for p in DEFAULT_PRESETS if p.id == "exec_summary"),
            None
        )
        assert exec_preset is not None
        assert "Executive" in exec_preset.name

    def test_arabic_view_preset_exists(self):
        """Test that Arabic view preset exists."""
        ar_preset = next(
            (p for p in DEFAULT_PRESETS if p.id == "arabic_view"),
            None
        )
        assert ar_preset is not None
        assert ar_preset.state.language == "ar"


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestShareableLinksIntegration:
    """Integration tests for shareable links."""

    def test_full_workflow_query_params(self):
        """Test complete workflow: create state -> generate URL -> parse back."""
        # Create state
        original = ViewState(
            year=2025,
            quarter=3,
            region="Eastern",
            language="en",
            pillar="environmental",
            compare_period=True,
            compare_region=False,
        )

        # Generate URL
        url = generate_share_url(original, "https://dashboard.example.com")

        # Extract params from URL
        from urllib.parse import parse_qs, urlparse
        parsed = urlparse(url)
        params = {k: v[0] for k, v in parse_qs(parsed.query).items()}

        # Restore state
        restored = ViewState.from_query_params(params)

        # Verify
        assert restored.year == original.year
        assert restored.quarter == original.quarter
        assert restored.region == original.region
        assert restored.pillar == original.pillar

    def test_full_workflow_encoded(self):
        """Test complete workflow with encoded state."""
        original = ViewState(
            year=2024,
            quarter=2,
            region="Madinah",
            language="ar",
        )

        # Encode
        encoded = original.to_encoded_state()

        # Decode
        restored = ViewState.from_encoded_state(encoded)

        # Verify
        assert restored.year == original.year
        assert restored.quarter == original.quarter
        assert restored.region == original.region
        assert restored.language == original.language
