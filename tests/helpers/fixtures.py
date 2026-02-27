"""Test fixtures and utilities for SessionIntent."""

import tempfile
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

# Default test apps
TEST_APPS = {
    "firefox": {
        "cmd": ["firefox", "-P", "{profile|default}"],
        "append_param": "urls",
        "internal_reuse": True,
    },
    "vscode": {
        "cmd": ["code", "--reuse-window", "{workspace|}"],
        "primary_param": "workspace",
        "internal_reuse": True,
    },
    "discord": {
        "cmd": ["discord"],
        "check": "discord",
        "flags": {"background": "--start-minimized"},
        "internal_reuse": False,
    },
}

# Default test config
TEST_CONFIG = {
    "version": 1,
    "defaults": {"ask_before_kill": True, "reuse_workspaces": True},
    "hardware_profiles": {
        "battery": {"disable_modes": ["gaming"]},
        "plugged": {"allow_all": True},
    },
    "modes": {
        "browsing": {
            "label": "Browsing",
            "firefox": {"profile": "browsing"},
            "workspaces": {"1": ["firefox"], "2": ["discord"]},
        },
        "work": {
            "label": "Work",
            "firefox": {"profile": "work"},
            "workspaces": {"1": ["firefox"], "2": ["vscode"]},
        },
    },
}


def create_temp_config(
    config_data: Optional[Dict[str, Any]] = None,
    apps_data: Optional[Dict[str, Any]] = None,
) -> tuple:
    """
    Create temporary config directory with test data.

    Args:
        config_data: Config dictionary (uses TEST_CONFIG if None)
        apps_data: Apps dictionary (uses TEST_APPS if None)

    Returns:
        Tuple of (temp_dir, config_path, apps_path)
    """
    temp_dir = Path(tempfile.mkdtemp())
    config_path = temp_dir / "config.yaml"
    apps_path = temp_dir / "apps.yaml"

    if config_data is None:
        config_data = TEST_CONFIG.copy()

    if apps_data is None:
        apps_data = TEST_APPS.copy()

    with open(config_path, "w") as f:
        yaml.dump(config_data, f)

    with open(apps_path, "w") as f:
        yaml.dump(apps_data, f)

    return temp_dir, config_path, apps_path


def create_temp_dir() -> Path:
    """Create a temporary directory and return its path."""
    return Path(tempfile.mkdtemp())


def mock_is_running(running_apps: list):
    """Create a mock is_running function."""

    def mock_func(pattern, dev_mode=False):
        if dev_mode:
            return False
        return pattern in running_apps

    return mock_func
