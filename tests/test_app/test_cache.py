"""
Tests for SessionIntent app cache functionality.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from src.app.cache import (
    CACHE_VERSION,
    DEFAULT_CACHE_TTL_DAYS,
    get_cache_age_days,
    get_cached_apps,
    get_cache_path,
    invalidate_cache,
    is_cache_valid,
    save_app_cache,
)


@pytest.fixture
def temp_state_dir(tmp_path: Path) -> Path:
    """Create a temporary state directory for testing."""
    state_dir = tmp_path / "sessionintent"
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


@pytest.fixture
def mock_state_dir(temp_state_dir: Path) -> None:
    """Patch STATE_DIR to use temporary directory."""
    with patch("src.app.cache.STATE_DIR", temp_state_dir):
        yield temp_state_dir


class TestCachePath:
    """Tests for cache path functionality."""

    def test_get_cache_path_creates_directory(self, mock_state_dir: Path) -> None:
        """Cache path should create directory if it doesn't exist."""
        cache_path = get_cache_path()
        assert cache_path.parent.exists()

    def test_cache_path_is_correct(self, mock_state_dir: Path) -> None:
        """Cache path should be in state directory."""
        cache_path = get_cache_path()
        assert cache_path.name == "cache_apps.json"
        assert cache_path.parent == mock_state_dir


class TestCacheValidity:
    """Tests for cache validation."""

    def test_is_cache_valid_no_file(self, mock_state_dir: Path) -> None:
        """Should return False when cache file doesn't exist."""
        assert is_cache_valid() is False

    def test_is_cache_valid_expired(self, mock_state_dir: Path) -> None:
        """Should return False when cache is expired."""
        old_timestamp = (datetime.now() - timedelta(days=DEFAULT_CACHE_TTL_DAYS + 1)).isoformat()
        cache_data = {
            "version": CACHE_VERSION,
            "timestamp": old_timestamp,
            "detected_apps": {"firefox": {"cmd": ["firefox"]}},
        }
        cache_path = mock_state_dir / "cache_apps.json"
        with open(cache_path, "w") as f:
            json.dump(cache_data, f)

        assert is_cache_valid() is False

    def test_is_cache_valid_wrong_version(self, mock_state_dir: Path) -> None:
        """Should return False when cache version doesn't match."""
        cache_data = {
            "version": 999,
            "timestamp": datetime.now().isoformat(),
            "detected_apps": {"firefox": {"cmd": ["firefox"]}},
        }
        cache_path = mock_state_dir / "cache_apps.json"
        with open(cache_path, "w") as f:
            json.dump(cache_data, f)

        assert is_cache_valid() is False

    def test_is_cache_valid_valid(self, mock_state_dir: Path) -> None:
        """Should return True when cache is valid."""
        cache_data = {
            "version": CACHE_VERSION,
            "timestamp": datetime.now().isoformat(),
            "detected_apps": {"firefox": {"cmd": ["firefox"]}},
        }
        cache_path = mock_state_dir / "cache_apps.json"
        with open(cache_path, "w") as f:
            json.dump(cache_data, f)

        assert is_cache_valid() is True

    def test_is_cache_valid_custom_ttl(self, mock_state_dir: Path) -> None:
        """Should respect custom TTL setting."""
        recent_timestamp = (datetime.now() - timedelta(days=1)).isoformat()
        cache_data = {
            "version": CACHE_VERSION,
            "timestamp": recent_timestamp,
            "detected_apps": {"firefox": {"cmd": ["firefox"]}},
        }
        cache_path = mock_state_dir / "cache_apps.json"
        with open(cache_path, "w") as f:
            json.dump(cache_data, f)

        assert is_cache_valid(ttl_days=7) is True
        assert is_cache_valid(ttl_days=0) is False


class TestCacheOperations:
    """Tests for cache save and load operations."""

    def test_save_and_get_cached_apps(self, mock_state_dir: Path) -> None:
        """Should save and retrieve cached apps correctly."""
        apps = {
            "firefox": {"cmd": ["firefox"], "check": "firefox"},
            "code": {"cmd": ["code"], "check": "code"},
        }
        save_app_cache(apps)

        cached = get_cached_apps()
        assert cached == apps

    def test_get_cached_apps_no_cache(self, mock_state_dir: Path) -> None:
        """Should return None when no cache exists."""
        assert get_cached_apps() is None

    def test_get_cached_apps_corrupted(self, mock_state_dir: Path) -> None:
        """Should return None when cache is corrupted."""
        cache_path = mock_state_dir / "cache_apps.json"
        with open(cache_path, "w") as f:
            f.write("not valid json{")

        assert get_cached_apps() is None


class TestCacheInvalidation:
    """Tests for cache invalidation."""

    def test_invalidate_removes_file(self, mock_state_dir: Path) -> None:
        """Should remove cache file when invalidating."""
        apps = {"firefox": {"cmd": ["firefox"]}}
        save_app_cache(apps)

        cache_path = mock_state_dir / "cache_apps.json"
        assert cache_path.exists()

        invalidate_cache()
        assert not cache_path.exists()

    def test_invalidate_nonexistent(self, mock_state_dir: Path) -> None:
        """Should return True when cache doesn't exist."""
        assert invalidate_cache() is True


class TestCacheAge:
    """Tests for cache age calculation."""

    def test_get_cache_age_no_file(self, mock_state_dir: Path) -> None:
        """Should return None when cache doesn't exist."""
        assert get_cache_age_days() is None

    def test_get_cache_age_valid(self, mock_state_dir: Path) -> None:
        """Should return correct age in days."""
        cache_data = {
            "version": CACHE_VERSION,
            "timestamp": datetime.now().isoformat(),
            "detected_apps": {"firefox": {"cmd": ["firefox"]}},
        }
        cache_path = mock_state_dir / "cache_apps.json"
        with open(cache_path, "w") as f:
            json.dump(cache_data, f)

        age = get_cache_age_days()
        assert age is not None
        assert age < 1

    def test_get_cache_age_old(self, mock_state_dir: Path) -> None:
        """Should return correct age for old cache."""
        old_timestamp = (datetime.now() - timedelta(days=5)).isoformat()
        cache_data = {
            "version": CACHE_VERSION,
            "timestamp": old_timestamp,
            "detected_apps": {"firefox": {"cmd": ["firefox"]}},
        }
        cache_path = mock_state_dir / "cache_apps.json"
        with open(cache_path, "w") as f:
            json.dump(cache_data, f)

        age = get_cache_age_days()
        assert age is not None
        assert 4 < age < 6