"""
Branding Configuration
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This module contains branding constants for the platform,
including author information for reports and presentations.
"""

from dataclasses import dataclass
from functools import lru_cache


@dataclass
class Branding:
    """
    Branding configuration for the Analytics Hub.

    Contains author information, platform branding,
    and ministry details for use in reports and exports.
    """

    # Platform branding
    platform_name: str = "Sustainable Economic Development Analytics Hub"
    platform_name_ar: str = "منصة تحليلات التنمية الاقتصادية المستدامة"
    platform_short_name: str = "Analytics Hub"
    platform_version: str = "1.0.0"

    # Primary client
    client_name: str = "Ministry of Economy and Planning"
    client_name_ar: str = "وزارة الاقتصاد والتخطيط"
    client_country: str = "Kingdom of Saudi Arabia"
    client_country_ar: str = "المملكة العربية السعودية"

    # Author information (for reports and presentations)
    author_name: str = "Eng. Sultan Albuqami"
    author_name_ar: str = "م. سلطان البقمي"
    author_mobile: str = "0553112800"
    author_email: str = "sultan_mutep@hotmail.com"

    # Logo paths (relative to assets folder)
    logo_path: str | None = None  # Can be set to actual logo file path
    logo_light_path: str | None = None
    logo_dark_path: str | None = None

    # Footer text
    footer_text: str = "© 2024 Ministry of Economy and Planning. All rights reserved."
    footer_text_ar: str = "© 2024 وزارة الاقتصاد والتخطيط. جميع الحقوق محفوظة."

    # Confidentiality notice
    confidentiality_notice: str = (
        "CONFIDENTIAL: This document contains proprietary information "
        "intended for authorized personnel only."
    )
    confidentiality_notice_ar: str = (
        "سري: هذه الوثيقة تحتوي على معلومات خاصة مخصصة للموظفين المصرح لهم فقط."
    )

    def get_author_info(self, language: str = "en") -> str:
        """Get formatted author information string."""
        if language == "ar":
            return f"{self.author_name_ar}\n{self.author_mobile}\n{self.author_email}"
        return f"{self.author_name}\n{self.author_mobile}\n{self.author_email}"

    def get_client_info(self, language: str = "en") -> str:
        """Get formatted client information string."""
        if language == "ar":
            return f"{self.client_name_ar}\n{self.client_country_ar}"
        return f"{self.client_name}\n{self.client_country}"

    def get_platform_title(self, language: str = "en") -> str:
        """Get platform title in specified language."""
        if language == "ar":
            return self.platform_name_ar
        return self.platform_name

    def get_footer(self, language: str = "en") -> str:
        """Get footer text in specified language."""
        if language == "ar":
            return self.footer_text_ar
        return self.footer_text

    def get_report_header(self, language: str = "en") -> dict:
        """Get complete header information for reports."""
        return {
            "platform_name": self.get_platform_title(language),
            "client": self.get_client_info(language),
            "author": self.get_author_info(language),
            "version": self.platform_version,
        }


# Global branding instance
_branding_instance: Branding | None = None


@lru_cache(maxsize=1)
def get_branding() -> Branding:
    """Get the global branding configuration."""
    global _branding_instance
    if _branding_instance is None:
        _branding_instance = Branding()
    return _branding_instance


# Convenience constant for backwards compatibility
# Use BRANDING['key'] to access branding values as a dictionary
def _get_branding_dict() -> dict:
    """Get branding configuration as a dictionary."""
    b = get_branding()
    return {
        "platform_name": b.platform_name,
        "platform_name_ar": b.platform_name_ar,
        "platform_short_name": b.platform_short_name,
        "platform_version": b.platform_version,
        "client_name": b.client_name,
        "client_name_ar": b.client_name_ar,
        "client_country": b.client_country,
        "client_country_ar": b.client_country_ar,
        "author_name": b.author_name,
        "author_name_ar": b.author_name_ar,
        "author_mobile": b.author_mobile,
        "author_email": b.author_email,
        "footer_text": b.footer_text,
        "footer_text_ar": b.footer_text_ar,
        "confidentiality_notice": b.confidentiality_notice,
        "confidentiality_notice_ar": b.confidentiality_notice_ar,
    }


BRANDING = _get_branding_dict()
