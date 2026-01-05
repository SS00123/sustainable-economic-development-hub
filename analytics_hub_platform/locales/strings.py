"""
Localization Strings Module
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

String dictionaries for English and Arabic localization.
"""

from analytics_hub_platform.locales.ar import STRINGS_AR
from analytics_hub_platform.locales.en import STRINGS_EN

# All available locales
LOCALES: dict[str, dict[str, str]] = {
    "en": STRINGS_EN,
    "ar": STRINGS_AR,
}

# Default locale
DEFAULT_LOCALE = "en"


def get_strings(language: str = "en") -> dict[str, str]:
    """
    Get all strings for a language.

    Args:
        language: Language code (en/ar)

    Returns:
        Dictionary of string key to translated value
    """
    return LOCALES.get(language, LOCALES[DEFAULT_LOCALE])


def get_string(key: str, language: str = "en", default: str | None = None) -> str:
    """
    Get a single string by key.

    Args:
        key: String key
        language: Language code
        default: Default value if key not found

    Returns:
        Translated string
    """
    strings = get_strings(language)
    return strings.get(key, default or key)


def get_available_languages() -> dict[str, str]:
    """
    Get available languages.

    Returns:
        Dictionary of language codes to display names
    """
    return {
        "en": "English",
        "ar": "العربية",
    }


def is_rtl(language: str) -> bool:
    """
    Check if language is right-to-left.

    Args:
        language: Language code

    Returns:
        True if RTL language
    """
    rtl_languages = {"ar", "he", "fa", "ur"}
    return language in rtl_languages


def format_number(value: float, language: str = "en", decimals: int = 2) -> str:
    """
    Format number according to locale.

    Args:
        value: Number to format
        language: Language code
        decimals: Decimal places

    Returns:
        Formatted number string
    """
    if language == "ar":
        # Arabic numerals (Eastern Arabic)
        arabic_numerals = "٠١٢٣٤٥٦٧٨٩"
        formatted = f"{value:,.{decimals}f}"
        result = ""
        for char in formatted:
            if char.isdigit():
                result += arabic_numerals[int(char)]
            elif char == ",":
                result += "٬"
            elif char == ".":
                result += "٫"
            else:
                result += char
        return result

    return f"{value:,.{decimals}f}"


def format_date(date_str: str, language: str = "en") -> str:
    """
    Format date according to locale.

    Args:
        date_str: ISO date string
        language: Language code

    Returns:
        Formatted date string
    """
    from datetime import datetime

    try:
        dt = datetime.fromisoformat(date_str)

        if language == "ar":
            # Arabic month names
            arabic_months = [
                "يناير",
                "فبراير",
                "مارس",
                "أبريل",
                "مايو",
                "يونيو",
                "يوليو",
                "أغسطس",
                "سبتمبر",
                "أكتوبر",
                "نوفمبر",
                "ديسمبر",
            ]
            return f"{dt.day} {arabic_months[dt.month - 1]} {dt.year}"

        return dt.strftime("%B %d, %Y")
    except ValueError:
        return date_str


def format_quarter(year: int, quarter: int, language: str = "en") -> str:
    """
    Format quarter label.

    Args:
        year: Year
        quarter: Quarter (1-4)
        language: Language code

    Returns:
        Formatted quarter string
    """
    if language == "ar":
        return f"الربع {quarter} {year}"
    return f"Q{quarter} {year}"
