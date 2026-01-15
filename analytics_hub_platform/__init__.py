"""
Analytics Hub Platform
Sustainable Economic Development Analytics Hub
Eng. Sultan Albuqami

Main package initialization.
"""

__version__ = "1.0.0"
__author__ = "Eng. Sultan Albuqami"
__email__ = "sultan_mutep@hotmail.com"

from analytics_hub_platform.config import get_config
from analytics_hub_platform.infrastructure import get_repository, get_settings

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "get_config",
    "get_settings",
    "get_repository",
]
