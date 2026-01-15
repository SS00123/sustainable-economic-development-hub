"""
Input Validation Utilities
Sustainable Economic Development Analytics Hub
Eng. Sultan Albuqami

Provides input validation decorators and sanitization functions.
"""

import functools
import logging
import re
from collections.abc import Callable
from typing import Any, TypeVar

from analytics_hub_platform.infrastructure.exceptions import ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T")


# ============================================
# VALIDATION DECORATORS
# ============================================


def validate_inputs(**validators: Callable[[Any], bool]) -> Callable:
    """
    Decorator to validate function inputs.

    Args:
        **validators: Mapping of parameter names to validator functions

    Example:
        @validate_inputs(
            year=lambda x: 2000 <= x <= 2100,
            quarter=lambda x: 1 <= x <= 4,
            region=lambda x: x in VALID_REGIONS,
        )
        def get_data(year: int, quarter: int, region: str):
            ...
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Get function parameter names
            import inspect

            sig = inspect.signature(func)
            params = list(sig.parameters.keys())

            # Build full kwargs from args and kwargs
            all_kwargs = {}
            for i, arg in enumerate(args):
                if i < len(params):
                    all_kwargs[params[i]] = arg
            all_kwargs.update(kwargs)

            # Validate each parameter
            errors = []
            for param_name, validator in validators.items():
                if param_name in all_kwargs:
                    value = all_kwargs[param_name]
                    if value is not None and not validator(value):
                        errors.append(f"Invalid value for '{param_name}': {value}")

            if errors:
                raise ValidationError("; ".join(errors))

            return func(*args, **kwargs)

        return wrapper

    return decorator


def validate_required(*required_params: str) -> Callable:
    """
    Decorator to ensure required parameters are not None.

    Args:
        *required_params: Names of required parameters

    Example:
        @validate_required('tenant_id', 'year')
        def get_data(tenant_id: str, year: int, quarter: Optional[int] = None):
            ...
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            import inspect

            sig = inspect.signature(func)
            params = list(sig.parameters.keys())

            # Build full kwargs
            all_kwargs = {}
            for i, arg in enumerate(args):
                if i < len(params):
                    all_kwargs[params[i]] = arg
            all_kwargs.update(kwargs)

            # Check required params
            missing = []
            for param in required_params:
                if param not in all_kwargs or all_kwargs[param] is None:
                    missing.append(param)

            if missing:
                raise ValidationError(f"Missing required parameters: {', '.join(missing)}")

            return func(*args, **kwargs)

        return wrapper

    return decorator


# ============================================
# SANITIZATION FUNCTIONS
# ============================================


def sanitize_string(
    value: str,
    max_length: int = 1000,
    strip_html: bool = True,
    strip_sql: bool = True,
) -> str:
    """
    Sanitize a string input.

    Args:
        value: Input string
        max_length: Maximum allowed length
        strip_html: Remove HTML tags
        strip_sql: Remove SQL injection patterns

    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        value = str(value)

    # Truncate to max length
    value = value[:max_length]

    # Strip HTML tags
    if strip_html:
        value = re.sub(r"<[^>]+>", "", value)

    # Strip SQL injection patterns
    if strip_sql:
        sql_patterns = [
            r";\s*--",
            r";\s*DROP",
            r";\s*DELETE",
            r";\s*INSERT",
            r";\s*UPDATE",
            r"'\s*OR\s+'",
            r"'\s*AND\s+'",
            r"UNION\s+SELECT",
            r"EXEC\s*\(",
        ]
        for pattern in sql_patterns:
            value = re.sub(pattern, "", value, flags=re.IGNORECASE)

    return value.strip()


def sanitize_tenant_id(tenant_id: str) -> str:
    """
    Sanitize and validate tenant ID.

    Args:
        tenant_id: Raw tenant ID

    Returns:
        Sanitized tenant ID

    Raises:
        ValidationError: If tenant ID is invalid
    """
    if not tenant_id:
        raise ValidationError("Tenant ID cannot be empty")

    # Allow only alphanumeric, underscore, hyphen
    sanitized = re.sub(r"[^a-zA-Z0-9_\-]", "", str(tenant_id))

    if len(sanitized) < 2:
        raise ValidationError("Tenant ID must be at least 2 characters")

    if len(sanitized) > 50:
        raise ValidationError("Tenant ID cannot exceed 50 characters")

    return sanitized


def sanitize_email(email: str) -> str:
    """
    Sanitize and validate email address.

    Args:
        email: Raw email address

    Returns:
        Sanitized email address

    Raises:
        ValidationError: If email is invalid
    """
    if not email:
        raise ValidationError("Email cannot be empty")

    email = email.strip().lower()

    # Basic email pattern
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        raise ValidationError(f"Invalid email format: {email}")

    return email


def validate_year(year: int | str) -> int:
    """
    Validate year value.

    Args:
        year: Year as int or string

    Returns:
        Validated year as int

    Raises:
        ValidationError: If year is invalid
    """
    try:
        year_int = int(year)
    except (ValueError, TypeError):
        raise ValidationError(f"Year must be a number: {year}")

    if year_int < 1900 or year_int > 2100:
        raise ValidationError(f"Year must be between 1900 and 2100: {year_int}")

    return year_int


def validate_quarter(quarter: int | str) -> int:
    """
    Validate quarter value.

    Args:
        quarter: Quarter as int or string

    Returns:
        Validated quarter as int

    Raises:
        ValidationError: If quarter is invalid
    """
    try:
        quarter_int = int(quarter)
    except (ValueError, TypeError):
        raise ValidationError(f"Quarter must be a number: {quarter}")

    if quarter_int < 1 or quarter_int > 4:
        raise ValidationError(f"Quarter must be between 1 and 4: {quarter_int}")

    return quarter_int


def validate_region(region: str, valid_regions: list[str]) -> str:
    """
    Validate region value.

    Args:
        region: Region name
        valid_regions: List of valid region names

    Returns:
        Validated region name

    Raises:
        ValidationError: If region is invalid
    """
    if not region:
        raise ValidationError("Region cannot be empty")

    region = region.strip()

    # Case-insensitive match
    for valid in valid_regions:
        if region.lower() == valid.lower():
            return valid

    raise ValidationError(
        f"Invalid region '{region}'. Must be one of: {', '.join(valid_regions[:5])}..."
    )


def validate_percentage(value: int | float | str, field_name: str = "Value") -> float:
    """
    Validate a percentage value (0-100).

    Args:
        value: Percentage value
        field_name: Name of field for error message

    Returns:
        Validated percentage as float

    Raises:
        ValidationError: If value is invalid
    """
    try:
        pct = float(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a number: {value}")

    if pct < 0 or pct > 100:
        raise ValidationError(f"{field_name} must be between 0 and 100: {pct}")

    return pct


def validate_positive_number(
    value: int | float | str,
    field_name: str = "Value",
    allow_zero: bool = True,
) -> float:
    """
    Validate a positive number.

    Args:
        value: Number value
        field_name: Name of field for error message
        allow_zero: Whether zero is allowed

    Returns:
        Validated number as float

    Raises:
        ValidationError: If value is invalid
    """
    try:
        num = float(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a number: {value}")

    if allow_zero:
        if num < 0:
            raise ValidationError(f"{field_name} must be non-negative: {num}")
    else:
        if num <= 0:
            raise ValidationError(f"{field_name} must be positive: {num}")

    return num


# ============================================
# COMPLEX VALIDATORS
# ============================================


def validate_filter_params(params: dict[str, Any]) -> dict[str, Any]:
    """
    Validate filter parameters.

    Args:
        params: Dictionary of filter parameters

    Returns:
        Validated and sanitized parameters

    Raises:
        ValidationError: If any parameter is invalid
    """
    validated = {}

    if "tenant_id" in params and params["tenant_id"]:
        validated["tenant_id"] = sanitize_tenant_id(params["tenant_id"])

    if "year" in params and params["year"] is not None:
        validated["year"] = validate_year(params["year"])

    if "quarter" in params and params["quarter"] is not None:
        validated["quarter"] = validate_quarter(params["quarter"])

    if "region" in params and params["region"]:
        # Note: Region validation requires valid_regions list
        validated["region"] = sanitize_string(params["region"], max_length=100)

    if "years" in params and params["years"]:
        validated["years"] = [validate_year(y) for y in params["years"]]

    if "regions" in params and params["regions"]:
        validated["regions"] = [sanitize_string(r, max_length=100) for r in params["regions"]]

    return validated


def validate_kpi_data(data: dict[str, Any]) -> dict[str, Any]:
    """
    Validate KPI data record.

    Args:
        data: KPI data dictionary

    Returns:
        Validated data dictionary

    Raises:
        ValidationError: If data is invalid
    """
    required_fields = ["year", "quarter", "region"]
    missing = [f for f in required_fields if f not in data or data[f] is None]

    if missing:
        raise ValidationError(f"Missing required KPI fields: {', '.join(missing)}")

    validated = {
        "year": validate_year(data["year"]),
        "quarter": validate_quarter(data["quarter"]),
        "region": sanitize_string(data["region"], max_length=100),
    }

    # Validate optional numeric fields
    numeric_fields = [
        "sustainability_index",
        "co2_per_gdp",
        "co2_per_capita",
        "renewable_energy_pct",
        "green_investment_pct",
        "gdp_growth",
        "employment_rate",
        "data_quality_score",
    ]

    for field in numeric_fields:
        if field in data and data[field] is not None:
            try:
                validated[field] = float(data[field])
            except (ValueError, TypeError):
                logger.warning(f"Invalid numeric value for {field}: {data[field]}")

    return validated
