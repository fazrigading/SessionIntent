"""
SessionIntent Logging System
Provides structured logging to file with rotation and level support.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from ..constants import LOG_DIR, LOG_FILE

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_logger: logging.Logger | None = None


def _get_logger() -> logging.Logger:
    """Get or create the singleton logger instance."""
    global _logger  # noqa: PLW0603

    if _logger is not None:
        return _logger

    _logger = logging.getLogger("sessionintent")
    _logger.setLevel(logging.INFO)

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    handler = logging.FileHandler(LOG_FILE)
    handler.setLevel(logging.INFO)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    _logger.addHandler(handler)
    _logger.propagate = False

    return _logger


def debug(message: str, **kwargs: Any) -> None:
    """Log debug message with optional context."""
    logger = _get_logger()
    if kwargs:
        message = f"{message} | {kwargs}"
    logger.debug(message)


def info(message: str, **kwargs: Any) -> None:
    """Log info message with optional context."""
    logger = _get_logger()
    if kwargs:
        message = f"{message} | {kwargs}"
    logger.info(message)


def warning(message: str, **kwargs: Any) -> None:
    """Log warning message with optional context."""
    logger = _get_logger()
    if kwargs:
        message = f"{message} | {kwargs}"
    logger.warning(message)


def error(message: str, **kwargs: Any) -> None:
    """Log error message with optional context."""
    logger = _get_logger()
    if kwargs:
        message = f"{message} | {kwargs}"
    logger.error(message)


def critical(message: str, **kwargs: Any) -> None:
    """Log critical message with optional context."""
    logger = _get_logger()
    if kwargs:
        message = f"{message} | {kwargs}"
    logger.critical(message)


def get_log_path() -> Path:
    """Get the path to the log file."""
    return LOG_FILE


def clear_log() -> int:
    """Clear the log file. Returns number of bytes cleared."""
    if not LOG_FILE.exists():
        return 0

    size = LOG_FILE.stat().st_size
    LOG_FILE.unlink()
    return size