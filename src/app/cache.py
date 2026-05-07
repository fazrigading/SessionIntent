"""
SessionIntent App Cache
Manages caching of detected applications to avoid expensive re-scans.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from ..constants import STATE_DIR


CACHE_VERSION = 1
DEFAULT_CACHE_TTL_DAYS = 14


def _get_cache_file() -> Path:
    """Get the path to the cache file, computing it each time for testability."""
    return STATE_DIR / "cache_apps.json"


def _ensure_cache_dir() -> None:
    """Ensure the cache directory exists."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def get_cache_path() -> Path:
    """Return the path to the cache file."""
    _ensure_cache_dir()
    return _get_cache_file()


def is_cache_valid(ttl_days: int = DEFAULT_CACHE_TTL_DAYS) -> bool:
    """
    Check if a valid cache exists and is not expired.

    Args:
        ttl_days: Number of days before cache expires.

    Returns:
        True if cache exists and is valid, False otherwise.
    """
    cache_path = get_cache_path()
    if not cache_path.exists():
        return False

    try:
        with open(cache_path, "r") as f:
            data = json.load(f)

        if data.get("version") != CACHE_VERSION:
            return False

        timestamp_str = data.get("timestamp")
        if not timestamp_str:
            return False

        cached_time = datetime.fromisoformat(timestamp_str)
        age = datetime.now() - cached_time

        return age < timedelta(days=ttl_days)
    except (json.JSONDecodeError, ValueError, OSError):
        return False


def get_cached_apps() -> dict[str, Any] | None:
    """
    Load cached detection results if valid.

    Returns:
        Dictionary of detected apps or None if cache invalid/missing.
    """
    if not is_cache_valid():
        return None

    cache_path = get_cache_path()
    try:
        with open(cache_path, "r") as f:
            data = json.load(f)
        return data.get("detected_apps", {})
    except (json.JSONDecodeError, OSError):
        return None


def save_app_cache(apps: dict[str, Any]) -> None:
    """
    Write detected apps to cache.

    Args:
        apps: Dictionary of detected applications.
    """
    cache_path = get_cache_path()
    data = {
        "version": CACHE_VERSION,
        "timestamp": datetime.now().isoformat(),
        "detected_apps": apps,
    }

    with open(cache_path, "w") as f:
        json.dump(data, f, indent=2)


def invalidate_cache() -> bool:
    """
    Delete the cache file if it exists.

    Returns:
        True if cache was deleted or didn't exist, False on error.
    """
    cache_path = get_cache_path()
    try:
        if cache_path.exists():
            cache_path.unlink()
        return True
    except OSError:
        return False


def get_cache_age_days() -> float | None:
    """
    Get the age of the cache in days.

    Returns:
        Age in days as float, or None if cache doesn't exist.
    """
    cache_path = get_cache_path()
    if not cache_path.exists():
        return None

    try:
        with open(cache_path, "r") as f:
            data = json.load(f)

        timestamp_str = data.get("timestamp")
        if not timestamp_str:
            return None

        cached_time = datetime.fromisoformat(timestamp_str)
        age = datetime.now() - cached_time
        return age.total_seconds() / 86400
    except (json.JSONDecodeError, ValueError, OSError):
        return None