"""
Custom Exceptions
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Centralized exception definitions for proper error handling.
"""

from typing import Any


class AnalyticsHubError(Exception):
    """Base exception for Analytics Hub platform."""

    def __init__(
        self,
        message: str,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.code = code or "INTERNAL_ERROR"
        self.details = details or {}
        super().__init__(self.message)


# ============================================
# AUTHENTICATION & AUTHORIZATION ERRORS
# ============================================


class AuthenticationError(AnalyticsHubError):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication required",
        code: str = "AUTH_REQUIRED",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, code, details)


class InvalidTokenError(AuthenticationError):
    """Raised when JWT token is invalid or expired."""

    def __init__(
        self,
        message: str = "Invalid or expired token",
        code: str = "INVALID_TOKEN",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, code, details)


class TokenExpiredError(AuthenticationError):
    """Raised when JWT token has expired."""

    def __init__(
        self,
        message: str = "Token has expired",
        code: str = "TOKEN_EXPIRED",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, code, details)


class AuthorizationError(AnalyticsHubError):
    """Raised when user lacks permission for an action."""

    def __init__(
        self,
        message: str = "Permission denied",
        code: str = "PERMISSION_DENIED",
        required_permission: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        details = details or {}
        if required_permission:
            details["required_permission"] = required_permission
        super().__init__(message, code, details)


# ============================================
# RATE LIMITING ERRORS
# ============================================


class RateLimitError(AnalyticsHubError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        code: str = "RATE_LIMITED",
        limit: int | None = None,
        window_seconds: int | None = None,
        retry_after: int | None = None,
        details: dict[str, Any] | None = None,
    ):
        details = details or {}
        if limit:
            details["limit"] = limit
        if window_seconds:
            details["window_seconds"] = window_seconds
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(message, code, details)


# ============================================
# VALIDATION ERRORS
# ============================================


class ValidationError(AnalyticsHubError):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str = "Validation error",
        code: str = "VALIDATION_ERROR",
        field: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        details = details or {}
        if field:
            details["field"] = field
        super().__init__(message, code, details)


class InvalidFilterError(ValidationError):
    """Raised when filter parameters are invalid."""

    def __init__(
        self,
        message: str = "Invalid filter parameters",
        code: str = "INVALID_FILTER",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, code, details=details)


# ============================================
# RESOURCE ERRORS
# ============================================


class NotFoundError(AnalyticsHubError):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        code: str = "NOT_FOUND",
        resource_type: str | None = None,
        resource_id: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        details = details or {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id
        super().__init__(message, code, details)


class TenantNotFoundError(NotFoundError):
    """Raised when tenant is not found."""

    def __init__(
        self,
        tenant_id: str,
        message: str | None = None,
    ):
        super().__init__(
            message=message or f"Tenant not found: {tenant_id}",
            code="TENANT_NOT_FOUND",
            resource_type="tenant",
            resource_id=tenant_id,
        )


class IndicatorNotFoundError(NotFoundError):
    """Raised when indicator is not found."""

    def __init__(
        self,
        indicator_id: str,
        message: str | None = None,
    ):
        super().__init__(
            message=message or f"Indicator not found: {indicator_id}",
            code="INDICATOR_NOT_FOUND",
            resource_type="indicator",
            resource_id=indicator_id,
        )


# ============================================
# DATA ERRORS
# ============================================


class DataError(AnalyticsHubError):
    """Raised when there's a data processing error."""

    def __init__(
        self,
        message: str = "Data processing error",
        code: str = "DATA_ERROR",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, code, details)


class DataQualityError(DataError):
    """Raised when data quality is insufficient."""

    def __init__(
        self,
        message: str = "Insufficient data quality",
        code: str = "DATA_QUALITY_ERROR",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, code, details)


# ============================================
# EXTERNAL SERVICE ERRORS
# ============================================


class ExternalServiceError(AnalyticsHubError):
    """Raised when an external service fails."""

    def __init__(
        self,
        message: str = "External service error",
        code: str = "EXTERNAL_SERVICE_ERROR",
        service_name: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        details = details or {}
        if service_name:
            details["service_name"] = service_name
        super().__init__(message, code, details)


class LLMServiceError(ExternalServiceError):
    """Raised when LLM service fails."""

    def __init__(
        self,
        message: str = "LLM service error",
        code: str = "LLM_ERROR",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, code, service_name="llm", details=details)


# ============================================
# ML / ANALYTICS ERRORS
# ============================================


class MLError(AnalyticsHubError):
    """Base exception for ML-related errors."""

    def __init__(
        self,
        message: str = "ML processing error",
        code: str = "ML_ERROR",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, code, details)


class InsufficientDataError(MLError):
    """Raised when there's not enough data for ML operations."""

    def __init__(
        self,
        message: str = "Insufficient data for analysis",
        code: str = "INSUFFICIENT_DATA",
        required_points: int | None = None,
        actual_points: int | None = None,
        details: dict[str, Any] | None = None,
    ):
        details = details or {}
        if required_points is not None:
            details["required_points"] = required_points
        if actual_points is not None:
            details["actual_points"] = actual_points
        super().__init__(message, code, details)


class ModelNotFittedError(MLError):
    """Raised when attempting to use an unfitted model."""

    def __init__(
        self,
        message: str = "Model must be fitted before use",
        code: str = "MODEL_NOT_FITTED",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, code, details)


class ForecastError(MLError):
    """Raised when forecasting fails."""

    def __init__(
        self,
        message: str = "Forecast generation failed",
        code: str = "FORECAST_ERROR",
        kpi_id: str | None = None,
        region_id: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        details = details or {}
        if kpi_id:
            details["kpi_id"] = kpi_id
        if region_id:
            details["region_id"] = region_id
        super().__init__(message, code, details)


class AnomalyDetectionError(MLError):
    """Raised when anomaly detection fails."""

    def __init__(
        self,
        message: str = "Anomaly detection failed",
        code: str = "ANOMALY_DETECTION_ERROR",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, code, details)


class ConstantSeriesError(MLError):
    """Raised when data has zero variance (all same values)."""

    def __init__(
        self,
        message: str = "Cannot analyze constant series (zero variance)",
        code: str = "CONSTANT_SERIES",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, code, details)


__all__ = [
    "AnalyticsHubError",
    "AuthenticationError",
    "InvalidTokenError",
    "TokenExpiredError",
    "AuthorizationError",
    "RateLimitError",
    "ValidationError",
    "InvalidFilterError",
    "NotFoundError",
    "TenantNotFoundError",
    "IndicatorNotFoundError",
    "DataError",
    "DataQualityError",
    "ExternalServiceError",
    "LLMServiceError",
    "MLError",
    "InsufficientDataError",
    "ModelNotFittedError",
    "ForecastError",
    "AnomalyDetectionError",
    "ConstantSeriesError",
]
