"""
Model Persistence Module
Sustainable Economic Development Analytics Hub
Eng. Sultan Albuqami

This module provides utilities for saving and loading ML models
with versioning, metadata tracking, and integrity checks.
"""

import hashlib
import json
import logging
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, TypeVar

try:
    import joblib

    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False
    joblib = None

from analytics_hub_platform.infrastructure.settings import get_settings

logger = logging.getLogger(__name__)

# Type variable for generic model loading
T = TypeVar("T")


class ModelPersistenceError(Exception):
    """Base exception for model persistence errors."""

    pass


class ModelNotFoundError(ModelPersistenceError):
    """Model file not found."""

    pass


class ModelIntegrityError(ModelPersistenceError):
    """Model integrity check failed."""

    pass


class ModelVersionError(ModelPersistenceError):
    """Model version incompatibility."""

    pass


@dataclass
class ModelMetadata:
    """Metadata for saved models."""

    model_id: str
    model_class: str
    model_type: str
    version: str
    created_at: str
    checksum: str
    parameters: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)
    training_info: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModelMetadata":
        """Create from dictionary."""
        return cls(**data)


def _check_joblib() -> None:
    """Check if joblib is available."""
    if not JOBLIB_AVAILABLE:
        raise ModelPersistenceError(
            "joblib is required for model persistence. Install with: pip install joblib"
        )


def _compute_checksum(file_path: Path) -> str:
    """Compute SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def _get_models_directory() -> Path:
    """Get the models storage directory."""
    settings = get_settings()

    # Use models directory from settings or default
    base_dir = getattr(settings, "models_directory", None)
    if base_dir is None:
        # Default to a 'models' subdirectory in the project
        base_dir = Path(__file__).parent.parent.parent / "models"
    else:
        base_dir = Path(base_dir)

    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir


def generate_model_id(
    model_type: str,
    kpi_id: str | None = None,
    region_id: str | None = None,
) -> str:
    """
    Generate a unique model identifier.

    Args:
        model_type: Type of model (e.g., "forecaster", "anomaly_detector")
        kpi_id: Optional KPI identifier
        region_id: Optional region identifier

    Returns:
        Unique model ID string
    """
    import uuid

    parts = [model_type]
    if kpi_id:
        parts.append(kpi_id)
    if region_id:
        parts.append(region_id)

    # Use timestamp with microseconds and UUID suffix for uniqueness
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    parts.append(timestamp)
    parts.append(uuid.uuid4().hex[:8])
    parts.append(timestamp)

    return "_".join(parts)


def save_model(
    model: Any,
    model_id: str,
    model_type: str = "forecaster",
    version: str = "1.0.0",
    parameters: dict[str, Any] | None = None,
    metrics: dict[str, float] | None = None,
    training_info: dict[str, Any] | None = None,
    overwrite: bool = False,
) -> Path:
    """
    Save a trained model with metadata.

    Args:
        model: The model object to save
        model_id: Unique identifier for the model
        model_type: Type of model (e.g., "forecaster", "anomaly_detector")
        version: Model version string (semver format)
        parameters: Model hyperparameters
        metrics: Training/validation metrics
        training_info: Additional training information
        overwrite: Whether to overwrite existing model

    Returns:
        Path to the saved model file

    Raises:
        ModelPersistenceError: If save fails
    """
    _check_joblib()

    models_dir = _get_models_directory()
    model_dir = models_dir / model_id

    if model_dir.exists() and not overwrite:
        raise ModelPersistenceError(
            f"Model '{model_id}' already exists. Use overwrite=True to replace."
        )

    model_dir.mkdir(parents=True, exist_ok=True)

    model_file = model_dir / "model.joblib"
    metadata_file = model_dir / "metadata.json"

    try:
        # Save model with compression
        joblib.dump(model, model_file, compress=3)

        # Compute checksum
        checksum = _compute_checksum(model_file)

        # Create metadata
        metadata = ModelMetadata(
            model_id=model_id,
            model_class=model.__class__.__name__,
            model_type=model_type,
            version=version,
            created_at=datetime.now().isoformat(),
            checksum=checksum,
            parameters=parameters or {},
            metrics=metrics or {},
            training_info=training_info or {},
        )

        # Save metadata
        with open(metadata_file, "w") as f:
            json.dump(metadata.to_dict(), f, indent=2)

        logger.info(f"Model saved successfully: {model_id}")
        return model_file

    except Exception as e:
        # Cleanup on failure
        if model_file.exists():
            model_file.unlink()
        if metadata_file.exists():
            metadata_file.unlink()
        raise ModelPersistenceError(f"Failed to save model: {e}") from e


def load_model(
    model_id: str,
    expected_class: type[T] | None = None,
    verify_checksum: bool = True,
) -> T:
    """
    Load a saved model.

    Args:
        model_id: Unique identifier for the model
        expected_class: Expected model class for validation
        verify_checksum: Whether to verify model integrity

    Returns:
        The loaded model object

    Raises:
        ModelNotFoundError: If model doesn't exist
        ModelIntegrityError: If checksum verification fails
        ModelPersistenceError: If load fails
    """
    _check_joblib()

    models_dir = _get_models_directory()
    model_dir = models_dir / model_id

    if not model_dir.exists():
        raise ModelNotFoundError(f"Model '{model_id}' not found")

    model_file = model_dir / "model.joblib"
    metadata_file = model_dir / "metadata.json"

    if not model_file.exists():
        raise ModelNotFoundError(f"Model file not found for '{model_id}'")

    # Load and verify metadata
    if metadata_file.exists():
        with open(metadata_file) as f:
            metadata_dict = json.load(f)
        metadata = ModelMetadata.from_dict(metadata_dict)

        # Verify checksum
        if verify_checksum:
            current_checksum = _compute_checksum(model_file)
            if current_checksum != metadata.checksum:
                raise ModelIntegrityError(
                    f"Model '{model_id}' checksum mismatch. The model file may be corrupted."
                )

    try:
        model = joblib.load(model_file)

        # Validate model class
        if expected_class is not None and not isinstance(model, expected_class):
            raise ModelPersistenceError(
                f"Expected {expected_class.__name__}, got {model.__class__.__name__}"
            )

        logger.info(f"Model loaded successfully: {model_id}")
        return model

    except Exception as e:
        if isinstance(e, (ModelNotFoundError, ModelIntegrityError, ModelPersistenceError)):
            raise
        raise ModelPersistenceError(f"Failed to load model: {e}") from e


def get_model_metadata(model_id: str) -> ModelMetadata:
    """
    Get metadata for a saved model.

    Args:
        model_id: Unique identifier for the model

    Returns:
        ModelMetadata object

    Raises:
        ModelNotFoundError: If model doesn't exist
    """
    models_dir = _get_models_directory()
    model_dir = models_dir / model_id
    metadata_file = model_dir / "metadata.json"

    if not metadata_file.exists():
        raise ModelNotFoundError(f"Metadata not found for model '{model_id}'")

    with open(metadata_file) as f:
        metadata_dict = json.load(f)

    return ModelMetadata.from_dict(metadata_dict)


def list_models(
    model_type: str | None = None,
    include_metadata: bool = True,
) -> dict[str, ModelMetadata | None]:
    """
    List all saved models.

    Args:
        model_type: Filter by model type
        include_metadata: Whether to include metadata

    Returns:
        Dictionary mapping model IDs to their metadata
    """
    models_dir = _get_models_directory()
    models = {}

    if not models_dir.exists():
        return models

    for model_dir in models_dir.iterdir():
        if not model_dir.is_dir():
            continue

        model_id = model_dir.name

        if include_metadata:
            try:
                metadata = get_model_metadata(model_id)

                # Filter by type if specified
                if model_type and metadata.model_type != model_type:
                    continue

                models[model_id] = metadata
            except ModelNotFoundError:
                models[model_id] = None
        else:
            models[model_id] = None

    return models


def delete_model(model_id: str) -> bool:
    """
    Delete a saved model.

    Args:
        model_id: Unique identifier for the model

    Returns:
        True if deleted successfully

    Raises:
        ModelNotFoundError: If model doesn't exist
    """
    import shutil

    models_dir = _get_models_directory()
    model_dir = models_dir / model_id

    if not model_dir.exists():
        raise ModelNotFoundError(f"Model '{model_id}' not found")

    try:
        shutil.rmtree(model_dir)
        logger.info(f"Model deleted: {model_id}")
        return True
    except Exception as e:
        raise ModelPersistenceError(f"Failed to delete model: {e}") from e


def export_model(
    model_id: str,
    output_path: str | Path,
) -> Path:
    """
    Export a model to a standalone archive.

    Args:
        model_id: Unique identifier for the model
        output_path: Path for the output archive

    Returns:
        Path to the exported archive
    """
    import shutil

    models_dir = _get_models_directory()
    model_dir = models_dir / model_id

    if not model_dir.exists():
        raise ModelNotFoundError(f"Model '{model_id}' not found")

    output_path = Path(output_path)

    # Create a zip archive
    archive_base = output_path.with_suffix("")
    shutil.make_archive(str(archive_base), "zip", model_dir)

    final_path = archive_base.with_suffix(".zip")
    logger.info(f"Model exported to: {final_path}")
    return final_path


def import_model(
    archive_path: str | Path,
    model_id: str | None = None,
    overwrite: bool = False,
) -> str:
    """
    Import a model from an archive.

    Args:
        archive_path: Path to the model archive
        model_id: Optional custom model ID (uses original if not provided)
        overwrite: Whether to overwrite existing model

    Returns:
        The model ID of the imported model
    """
    import shutil
    import zipfile

    archive_path = Path(archive_path)

    if not archive_path.exists():
        raise ModelNotFoundError(f"Archive not found: {archive_path}")

    models_dir = _get_models_directory()

    # Extract to temp directory first to read metadata
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        with zipfile.ZipFile(archive_path, "r") as zf:
            zf.extractall(temp_path)

        # Read metadata to get original model ID
        metadata_file = temp_path / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                metadata = json.load(f)
            original_id = metadata.get("model_id", archive_path.stem)
        else:
            original_id = archive_path.stem

        # Use provided model_id or original
        final_id = model_id or original_id
        target_dir = models_dir / final_id

        if target_dir.exists() and not overwrite:
            raise ModelPersistenceError(
                f"Model '{final_id}' already exists. Use overwrite=True to replace."
            )

        # Copy to models directory
        if target_dir.exists():
            shutil.rmtree(target_dir)
        shutil.copytree(temp_path, target_dir)

        # Update model_id in metadata if changed
        if model_id and model_id != original_id:
            new_metadata_file = target_dir / "metadata.json"
            if new_metadata_file.exists():
                with open(new_metadata_file) as f:
                    metadata = json.load(f)
                metadata["model_id"] = model_id
                with open(new_metadata_file, "w") as f:
                    json.dump(metadata, f, indent=2)

    logger.info(f"Model imported: {final_id}")
    return final_id


class ModelRegistry:
    """
    Central registry for managing trained models.

    Provides a high-level interface for model lifecycle management
    including versioning and retrieval of the latest models.
    """

    def __init__(self):
        self._cache: dict[str, Any] = {}

    def register(
        self,
        model: Any,
        model_type: str,
        kpi_id: str | None = None,
        region_id: str | None = None,
        version: str = "1.0.0",
        parameters: dict[str, Any] | None = None,
        metrics: dict[str, float] | None = None,
    ) -> str:
        """
        Register a trained model.

        Args:
            model: The trained model
            model_type: Type of model
            kpi_id: Optional KPI identifier
            region_id: Optional region identifier
            version: Model version
            parameters: Model parameters
            metrics: Training metrics

        Returns:
            The assigned model ID
        """
        model_id = generate_model_id(model_type, kpi_id, region_id)

        save_model(
            model=model,
            model_id=model_id,
            model_type=model_type,
            version=version,
            parameters=parameters,
            metrics=metrics,
            training_info={
                "kpi_id": kpi_id,
                "region_id": region_id,
            },
        )

        # Cache the model
        self._cache[model_id] = model

        return model_id

    def get(
        self,
        model_id: str,
        use_cache: bool = True,
    ) -> Any:
        """
        Retrieve a model by ID.

        Args:
            model_id: The model identifier
            use_cache: Whether to use cached model

        Returns:
            The model object
        """
        if use_cache and model_id in self._cache:
            return self._cache[model_id]

        model = load_model(model_id)
        self._cache[model_id] = model
        return model

    def get_latest(
        self,
        model_type: str,
        kpi_id: str | None = None,
        region_id: str | None = None,
    ) -> Any | None:
        """
        Get the latest version of a model.

        Args:
            model_type: Type of model
            kpi_id: Optional KPI filter
            region_id: Optional region filter

        Returns:
            The latest model or None
        """
        models = list_models(model_type=model_type, include_metadata=True)

        if not models:
            return None

        # Filter by KPI and region
        filtered = {}
        for model_id, metadata in models.items():
            if metadata is None:
                continue

            training_info = metadata.training_info or {}

            if kpi_id and training_info.get("kpi_id") != kpi_id:
                continue
            if region_id and training_info.get("region_id") != region_id:
                continue

            filtered[model_id] = metadata

        if not filtered:
            return None

        # Sort by creation date and get latest
        sorted_models = sorted(
            filtered.items(),
            key=lambda x: x[1].created_at,
            reverse=True,
        )

        latest_id = sorted_models[0][0]
        return self.get(latest_id)

    def clear_cache(self):
        """Clear the model cache."""
        self._cache.clear()


# Global model registry instance
_model_registry: ModelRegistry | None = None


def get_model_registry() -> ModelRegistry:
    """Get the global model registry instance."""
    global _model_registry
    if _model_registry is None:
        _model_registry = ModelRegistry()
    return _model_registry
