"""
Logging Configuration
Sustainable Economic Development Analytics Hub
Eng. Sultan Albuqami

Centralized logging configuration for the platform.
Provides consistent log formatting across all modules.
"""

import logging
import sys
from pathlib import Path

from analytics_hub_platform.infrastructure.settings import get_settings


# Custom formatter with colors for console
class ColoredFormatter(logging.Formatter):
    """Colored log formatter for console output."""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"

        return super().format(record)


def setup_logging(
    level: str | None = None, log_file: str | None = None, use_colors: bool = True
) -> None:
    """
    Set up logging configuration for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        use_colors: Whether to use colored output for console
    """
    settings = get_settings()

    level = level or settings.log_level
    log_file = log_file or settings.log_file

    # Convert level string to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers
    root_logger.handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)

    if use_colors and sys.stdout.isatty():
        console_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        console_handler.setFormatter(ColoredFormatter(console_format))
    else:
        console_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        console_handler.setFormatter(logging.Formatter(console_format))

    root_logger.addHandler(console_handler)

    # File handler (if configured)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(numeric_level)
        file_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        file_handler.setFormatter(logging.Formatter(file_format))

        root_logger.addHandler(file_handler)

    # Set levels for noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

    logging.info(f"Logging configured at level: {level}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.

    Args:
        name: Logger name (usually __name__ of the module)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Initialize logging on module import
def _init_default_logging():
    """Initialize with default settings if not already configured."""
    root = logging.getLogger()
    if not root.handlers:
        setup_logging()


_init_default_logging()
