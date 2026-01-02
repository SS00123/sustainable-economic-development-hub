"""
Model Persistence Tests
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Tests for model saving, loading, and versioning.
"""

import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Skip all tests if joblib is not available
joblib = pytest.importorskip("joblib")


@pytest.fixture
def temp_models_dir():
    """Create a temporary models directory."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_settings(temp_models_dir):
    """Mock settings to use temp directory."""
    mock = MagicMock()
    mock.models_directory = str(temp_models_dir)

    with patch("analytics_hub_platform.domain.model_persistence.get_settings", return_value=mock):
        yield mock


class DummyModel:
    """Dummy model for testing."""

    def __init__(self, value: int = 42):
        self.value = value
        self.fitted = False

    def fit(self):
        self.fitted = True
        return self

    def predict(self, x):
        return [self.value] * len(x)


class TestModelMetadata:
    """Test ModelMetadata dataclass."""

    def test_metadata_creation(self):
        """Test creating model metadata."""
        from analytics_hub_platform.domain.model_persistence import ModelMetadata

        metadata = ModelMetadata(
            model_id="test_model_001",
            model_class="KPIForecaster",
            model_type="forecaster",
            version="1.0.0",
            created_at="2024-01-15T10:30:00",
            checksum="abc123",
            parameters={"n_estimators": 100},
            metrics={"rmse": 0.05},
            training_info={"kpi_id": "gdp_growth"},
        )

        assert metadata.model_id == "test_model_001"
        assert metadata.version == "1.0.0"
        assert metadata.parameters["n_estimators"] == 100

    def test_metadata_to_dict(self):
        """Test converting metadata to dictionary."""
        from analytics_hub_platform.domain.model_persistence import ModelMetadata

        metadata = ModelMetadata(
            model_id="test_model",
            model_class="DummyModel",
            model_type="test",
            version="1.0.0",
            created_at="2024-01-15T10:30:00",
            checksum="abc123",
        )

        data = metadata.to_dict()

        assert isinstance(data, dict)
        assert data["model_id"] == "test_model"
        assert data["version"] == "1.0.0"

    def test_metadata_from_dict(self):
        """Test creating metadata from dictionary."""
        from analytics_hub_platform.domain.model_persistence import ModelMetadata

        data = {
            "model_id": "test_model",
            "model_class": "DummyModel",
            "model_type": "test",
            "version": "2.0.0",
            "created_at": "2024-01-15T10:30:00",
            "checksum": "def456",
            "parameters": {},
            "metrics": {},
            "training_info": {},
        }

        metadata = ModelMetadata.from_dict(data)

        assert metadata.model_id == "test_model"
        assert metadata.version == "2.0.0"


class TestModelIdGeneration:
    """Test model ID generation."""

    def test_generate_model_id_basic(self):
        """Test basic model ID generation."""
        from analytics_hub_platform.domain.model_persistence import generate_model_id

        model_id = generate_model_id("forecaster")

        assert "forecaster" in model_id
        assert len(model_id) > 10

    def test_generate_model_id_with_kpi(self):
        """Test model ID with KPI."""
        from analytics_hub_platform.domain.model_persistence import generate_model_id

        model_id = generate_model_id("forecaster", kpi_id="gdp_growth")

        assert "forecaster" in model_id
        assert "gdp_growth" in model_id

    def test_generate_model_id_with_region(self):
        """Test model ID with region."""
        from analytics_hub_platform.domain.model_persistence import generate_model_id

        model_id = generate_model_id("forecaster", kpi_id="gdp", region_id="riyadh")

        assert "forecaster" in model_id
        assert "gdp" in model_id
        assert "riyadh" in model_id

    def test_unique_model_ids(self):
        """Test that generated IDs are unique."""
        from analytics_hub_platform.domain.model_persistence import generate_model_id

        id1 = generate_model_id("forecaster")
        id2 = generate_model_id("forecaster")

        # IDs should be different due to UUID suffix
        assert id1 != id2


class TestSaveModel:
    """Test model saving functionality."""

    def test_save_model_success(self, mock_settings, temp_models_dir):
        """Test successful model save."""
        from analytics_hub_platform.domain.model_persistence import save_model

        model = DummyModel(value=100)

        result = save_model(
            model=model,
            model_id="test_save_001",
            model_type="forecaster",
            version="1.0.0",
        )

        assert result.exists()
        assert result.name == "model.joblib"

        # Check metadata was created
        metadata_file = result.parent / "metadata.json"
        assert metadata_file.exists()

    def test_save_model_with_parameters(self, mock_settings, temp_models_dir):
        """Test saving model with parameters."""
        from analytics_hub_platform.domain.model_persistence import get_model_metadata, save_model

        model = DummyModel()

        save_model(
            model=model,
            model_id="test_params_001",
            model_type="forecaster",
            parameters={"n_estimators": 200, "max_depth": 5},
            metrics={"rmse": 0.03, "r2": 0.95},
        )

        metadata = get_model_metadata("test_params_001")

        assert metadata.parameters["n_estimators"] == 200
        assert metadata.metrics["rmse"] == 0.03

    def test_save_model_no_overwrite(self, mock_settings, temp_models_dir):
        """Test that save fails if model exists and overwrite=False."""
        from analytics_hub_platform.domain.model_persistence import (
            ModelPersistenceError,
            save_model,
        )

        model = DummyModel()

        save_model(model=model, model_id="test_no_overwrite")

        with pytest.raises(ModelPersistenceError, match="already exists"):
            save_model(model=model, model_id="test_no_overwrite")

    def test_save_model_with_overwrite(self, mock_settings, temp_models_dir):
        """Test overwriting an existing model."""
        from analytics_hub_platform.domain.model_persistence import load_model, save_model

        model1 = DummyModel(value=1)
        model2 = DummyModel(value=2)

        save_model(model=model1, model_id="test_overwrite")
        save_model(model=model2, model_id="test_overwrite", overwrite=True)

        loaded = load_model("test_overwrite")
        assert loaded.value == 2


class TestLoadModel:
    """Test model loading functionality."""

    def test_load_model_success(self, mock_settings, temp_models_dir):
        """Test successful model load."""
        from analytics_hub_platform.domain.model_persistence import load_model, save_model

        original = DummyModel(value=99)
        save_model(model=original, model_id="test_load_001")

        loaded = load_model("test_load_001")

        assert loaded.value == original.value

    def test_load_model_not_found(self, mock_settings, temp_models_dir):
        """Test loading non-existent model."""
        from analytics_hub_platform.domain.model_persistence import ModelNotFoundError, load_model

        with pytest.raises(ModelNotFoundError):
            load_model("nonexistent_model")

    def test_load_model_with_expected_class(self, mock_settings, temp_models_dir):
        """Test loading with expected class validation."""
        from analytics_hub_platform.domain.model_persistence import (
            ModelPersistenceError,
            load_model,
            save_model,
        )

        model = DummyModel()
        save_model(model=model, model_id="test_class_check")

        # Should work with correct class
        loaded = load_model("test_class_check", expected_class=DummyModel)
        assert isinstance(loaded, DummyModel)

        # Should fail with wrong class
        with pytest.raises(ModelPersistenceError, match="Expected"):
            load_model("test_class_check", expected_class=dict)

    def test_checksum_verification(self, mock_settings, temp_models_dir):
        """Test checksum verification on load."""
        from analytics_hub_platform.domain.model_persistence import (
            ModelIntegrityError,
            load_model,
            save_model,
        )

        model = DummyModel()
        save_model(model=model, model_id="test_checksum")

        # Corrupt the model file
        model_file = temp_models_dir / "test_checksum" / "model.joblib"
        with open(model_file, "ab") as f:
            f.write(b"corruption")

        with pytest.raises(ModelIntegrityError, match="checksum"):
            load_model("test_checksum", verify_checksum=True)

    def test_skip_checksum_verification(self, mock_settings, temp_models_dir):
        """Test loading without checksum verification."""
        from analytics_hub_platform.domain.model_persistence import load_model, save_model

        model = DummyModel()
        save_model(model=model, model_id="test_no_checksum")

        # Even if we corrupt metadata, load should work without verification
        metadata_file = temp_models_dir / "test_no_checksum" / "metadata.json"
        with open(metadata_file) as f:
            metadata = json.load(f)
        metadata["checksum"] = "wrong_checksum"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f)

        # Should load without error when verification is disabled
        loaded = load_model("test_no_checksum", verify_checksum=False)
        assert isinstance(loaded, DummyModel)


class TestListModels:
    """Test model listing functionality."""

    def test_list_models_empty(self, mock_settings, temp_models_dir):
        """Test listing when no models exist."""
        from analytics_hub_platform.domain.model_persistence import list_models

        models = list_models()
        assert len(models) == 0

    def test_list_models_with_models(self, mock_settings, temp_models_dir):
        """Test listing multiple models."""
        from analytics_hub_platform.domain.model_persistence import list_models, save_model

        save_model(DummyModel(), model_id="model_a", model_type="forecaster")
        save_model(DummyModel(), model_id="model_b", model_type="forecaster")
        save_model(DummyModel(), model_id="model_c", model_type="anomaly")

        models = list_models()

        assert len(models) == 3
        assert "model_a" in models
        assert "model_b" in models
        assert "model_c" in models

    def test_list_models_by_type(self, mock_settings, temp_models_dir):
        """Test filtering models by type."""
        from analytics_hub_platform.domain.model_persistence import list_models, save_model

        save_model(DummyModel(), model_id="forecast_1", model_type="forecaster")
        save_model(DummyModel(), model_id="forecast_2", model_type="forecaster")
        save_model(DummyModel(), model_id="anomaly_1", model_type="anomaly")

        forecasters = list_models(model_type="forecaster")

        assert len(forecasters) == 2
        assert "forecast_1" in forecasters
        assert "forecast_2" in forecasters
        assert "anomaly_1" not in forecasters


class TestDeleteModel:
    """Test model deletion functionality."""

    def test_delete_model_success(self, mock_settings, temp_models_dir):
        """Test successful model deletion."""
        from analytics_hub_platform.domain.model_persistence import (
            delete_model,
            list_models,
            save_model,
        )

        save_model(DummyModel(), model_id="to_delete")

        assert "to_delete" in list_models()

        result = delete_model("to_delete")

        assert result is True
        assert "to_delete" not in list_models()

    def test_delete_nonexistent_model(self, mock_settings, temp_models_dir):
        """Test deleting non-existent model."""
        from analytics_hub_platform.domain.model_persistence import ModelNotFoundError, delete_model

        with pytest.raises(ModelNotFoundError):
            delete_model("nonexistent")


class TestExportImportModel:
    """Test model export/import functionality."""

    def test_export_model(self, mock_settings, temp_models_dir):
        """Test exporting a model to archive."""
        from analytics_hub_platform.domain.model_persistence import export_model, save_model

        model = DummyModel(value=123)
        save_model(model, model_id="export_test")

        export_path = temp_models_dir / "exported"
        result = export_model("export_test", export_path)

        assert result.exists()
        assert result.suffix == ".zip"

    def test_import_model(self, mock_settings, temp_models_dir):
        """Test importing a model from archive."""
        from analytics_hub_platform.domain.model_persistence import (
            delete_model,
            export_model,
            import_model,
            load_model,
            save_model,
        )

        # Create and export model
        original = DummyModel(value=456)
        save_model(original, model_id="import_test")

        export_path = temp_models_dir / "to_import"
        archive = export_model("import_test", export_path)

        # Delete original
        delete_model("import_test")

        # Import from archive
        imported_id = import_model(archive)

        loaded = load_model(imported_id)
        assert loaded.value == 456

    def test_import_with_custom_id(self, mock_settings, temp_models_dir):
        """Test importing with custom model ID."""
        from analytics_hub_platform.domain.model_persistence import (
            export_model,
            import_model,
            list_models,
            save_model,
        )

        save_model(DummyModel(), model_id="original_id")
        archive = export_model("original_id", temp_models_dir / "custom_export")

        imported_id = import_model(archive, model_id="custom_new_id")

        assert imported_id == "custom_new_id"
        assert "custom_new_id" in list_models()


class TestModelRegistry:
    """Test ModelRegistry class."""

    def test_registry_register(self, mock_settings, temp_models_dir):
        """Test registering a model."""
        from analytics_hub_platform.domain.model_persistence import ModelRegistry

        registry = ModelRegistry()
        model = DummyModel(value=789)

        model_id = registry.register(
            model=model,
            model_type="forecaster",
            kpi_id="gdp_growth",
            region_id="riyadh",
        )

        assert "forecaster" in model_id
        assert "gdp_growth" in model_id

    def test_registry_get(self, mock_settings, temp_models_dir):
        """Test retrieving a model from registry."""
        from analytics_hub_platform.domain.model_persistence import ModelRegistry

        registry = ModelRegistry()
        original = DummyModel(value=111)

        model_id = registry.register(original, model_type="test")
        retrieved = registry.get(model_id)

        assert retrieved.value == 111

    def test_registry_cache(self, mock_settings, temp_models_dir):
        """Test registry caching."""
        from analytics_hub_platform.domain.model_persistence import ModelRegistry

        registry = ModelRegistry()
        model = DummyModel()
        model_id = registry.register(model, model_type="test")

        # First get should cache
        first = registry.get(model_id, use_cache=True)
        second = registry.get(model_id, use_cache=True)

        # Should be same object from cache
        assert first is second

    def test_registry_clear_cache(self, mock_settings, temp_models_dir):
        """Test clearing registry cache."""
        from analytics_hub_platform.domain.model_persistence import ModelRegistry

        registry = ModelRegistry()
        model = DummyModel()
        model_id = registry.register(model, model_type="test")

        registry.get(model_id)  # Cache it
        registry.clear_cache()

        # After clearing, cache should be empty
        assert len(registry._cache) == 0

    def test_registry_get_latest(self, mock_settings, temp_models_dir):
        """Test getting latest model."""
        from analytics_hub_platform.domain.model_persistence import ModelRegistry

        registry = ModelRegistry()

        # Register multiple models with unique IDs (no time.sleep needed)
        registry.register(DummyModel(value=1), model_type="forecaster", kpi_id="gdp")
        registry.register(DummyModel(value=2), model_type="forecaster", kpi_id="gdp")
        registry.register(DummyModel(value=3), model_type="forecaster", kpi_id="gdp")

        latest = registry.get_latest(model_type="forecaster", kpi_id="gdp")

        # Latest should be value=3 (registered last)
        assert latest is not None
        assert latest.value == 3


class TestGlobalRegistry:
    """Test global registry singleton."""

    def test_get_model_registry(self, mock_settings):
        """Test getting global registry."""
        from analytics_hub_platform.domain.model_persistence import get_model_registry

        registry1 = get_model_registry()
        registry2 = get_model_registry()

        assert registry1 is registry2
