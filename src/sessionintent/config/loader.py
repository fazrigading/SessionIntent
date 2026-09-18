"""
SessionIntent Configuration Loader
Loads and merges configuration from multiple sources:
1. System defaults (/usr/share/sessionintent/)
2. Local dev files (apps.yaml in current directory)
3. User config (~/.config/sessionintent/)
"""

from __future__ import annotations

import yaml
from pathlib import Path
from typing import Any

from ..constants import (
    CONFIG_DIR,
    CONFIG_PATH,
    APPS_PATH,
    SYSTEM_APPS_PATH,
    DEFAULT_CONFIG,
    DEFAULT_APPS,
)


def load_yaml_file(file_path: Path, default_content: str = "") -> dict[str, Any]:
    """Load a YAML file, returning empty dict if file doesn't exist or is invalid."""
    if not file_path.exists():
        return {}

    try:
        with open(file_path, "r") as f:
            content = yaml.safe_load(f)
            return content if content else {}
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {file_path}: {e}")
    except Exception as e:
        raise IOError(f"Error reading {file_path}: {e}")


def load_config(config_path: str | None = None) -> dict[str, Any]:
    """Load session configuration from file or return empty dict if not found."""
    path = Path(config_path) if config_path else CONFIG_PATH

    if not path.exists():
        return {}

    return load_yaml_file(path)


def load_apps() -> dict[str, Any]:
    """Load app registry from system and user sources, merging with user taking precedence."""
    bundled_apps = {}

    # Load system apps
    if SYSTEM_APPS_PATH.exists():
        bundled_apps = load_yaml_file(SYSTEM_APPS_PATH)

    # Check current directory for dev purposes (local override)
    local_dev_apps = Path("apps.yaml")
    if local_dev_apps.exists():
        local_apps = load_yaml_file(local_dev_apps)
        bundled_apps.update(local_apps)

    # Load user apps (overrides bundled)
    user_apps = {}
    if APPS_PATH.exists():
        user_apps = load_yaml_file(APPS_PATH)

    # Merge: bundled first, then user (user overrides bundled)
    return {**bundled_apps, **user_apps}


def init_default_configs() -> None:
    """Create default configuration files if they don't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if not CONFIG_PATH.exists():
        with open(CONFIG_PATH, "w") as f:
            f.write(DEFAULT_CONFIG)

    if not APPS_PATH.exists():
        with open(APPS_PATH, "w") as f:
            f.write(DEFAULT_APPS)
