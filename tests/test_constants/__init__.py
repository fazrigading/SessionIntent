"""Tests for constants package."""

import pytest
from pathlib import Path

from src.constants.paths import (
    CONFIG_DIR,
    SYSTEM_CONFIG_DIR,
    STATE_DIR,
    CONFIG_PATH,
    APPS_PATH,
    SYSTEM_APPS_PATH,
    STATE_FILE,
    AC_PATH,
)


class TestPaths:
    """Test path constants."""

    def test_config_dir_exists(self):
        """Test CONFIG_DIR is a Path object."""
        assert isinstance(CONFIG_DIR, Path)

    def test_config_path_is_correct(self):
        """Test CONFIG_PATH points to config.yaml."""
        assert CONFIG_PATH.name == "config.yaml"
        assert CONFIG_PATH.parent == CONFIG_DIR

    def test_apps_path_is_correct(self):
        """Test APPS_PATH points to apps.yaml."""
        assert APPS_PATH.name == "apps.yaml"
        assert APPS_PATH.parent == CONFIG_DIR

    def test_state_file_includes_current(self):
        """Test STATE_FILE includes current file."""
        assert STATE_FILE.name == "current"
        assert STATE_FILE.parent == STATE_DIR

    def test_ac_path_is_correct(self):
        """Test AC_PATH points to correct system path."""
        assert AC_PATH == "/sys/class/power_supply/AC/online"


class TestDefaults:
    """Test default values."""

    def test_default_apps_is_string(self):
        """Test DEFAULT_APPS is a string."""
        from src.constants.defaults import DEFAULT_APPS

        assert isinstance(DEFAULT_APPS, str)
        assert "firefox" in DEFAULT_APPS
        assert "vscode" in DEFAULT_APPS

    def test_default_config_is_string(self):
        """Test DEFAULT_CONFIG is a string."""
        from src.constants.defaults import DEFAULT_CONFIG

        assert isinstance(DEFAULT_CONFIG, str)
        assert "modes" in DEFAULT_CONFIG
        assert "browsing" in DEFAULT_CONFIG
