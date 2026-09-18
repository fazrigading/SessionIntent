"""
SessionIntent Configuration Validator
Validates config and apps files to catch errors early.
"""

from __future__ import annotations

import yaml
from pathlib import Path
from typing import Any


# Schema definition for config.yaml
CONFIG_SCHEMA = {
    "version": {"type": int, "required": False},
    "defaults": {
        "type": dict,
        "required": False,
        "keys": {
            "ask_before_kill": {"type": bool, "required": False},
            "reuse_workspaces": {"type": bool, "required": False},
            "wait_window": {"type": int, "required": False},
        },
    },
    "hardware_profiles": {
        "type": dict,
        "required": False,
        "keys": {
            "battery": {
                "type": dict,
                "required": False,
                "keys": {
                    "disable_modes": {"type": list, "required": False},
                },
            },
            "plugged": {
                "type": dict,
                "required": False,
                "keys": {
                    "allow_all": {"type": bool, "required": False},
                },
            },
        },
    },
    "modes": {
        "type": dict,
        "required": True,
        "min_items": 1,
    },
}

# Schema definition for apps.yaml
APPS_SCHEMA = {
    "required": True,
    "min_items": 1,
}


def validate_config(config: dict[str, Any]) -> list[str]:
    """Validate configuration dictionary against schema. Returns list of errors."""
    errors = []

    if not config:
        errors.append("Configuration is empty")
        return errors

    # Check required top-level keys
    if "modes" not in config:
        errors.append("Missing required key: 'modes'")

    # Validate defaults if present
    if "defaults" in config:
        defaults = config["defaults"]
        if not isinstance(defaults, dict):
            errors.append("'defaults' must be a dictionary")

    # Validate hardware_profiles if present
    if "hardware_profiles" in config:
        profiles = config["hardware_profiles"]
        if not isinstance(profiles, dict):
            errors.append("'hardware_profiles' must be a dictionary")

    # Validate modes if present
    if "modes" in config:
        modes = config["modes"]
        if not isinstance(modes, dict):
            errors.append("'modes' must be a dictionary")
        elif len(modes) == 0:
            errors.append("'modes' must contain at least one mode")
        else:
            for mode_name, mode_cfg in modes.items():
                if not isinstance(mode_cfg, dict):
                    errors.append(f"Mode '{mode_name}' must be a dictionary")
                    continue
                workspaces = mode_cfg.get("workspaces", {})
                if not isinstance(workspaces, dict):
                    errors.append(f"Mode '{mode_name}': 'workspaces' must be a dictionary")
                    continue
                for ws_num, ws_value in workspaces.items():
                    ws_errors = _validate_workspace_entry(f"Mode '{mode_name}', workspace '{ws_num}'", ws_value)
                    errors.extend(ws_errors)

    return errors


def validate_apps(apps: dict[str, Any]) -> list[str]:
    """Validate app registry dictionary against schema. Returns list of errors."""
    errors = []

    if not apps:
        errors.append("Application registry is empty")
        return errors

    if not isinstance(apps, dict):
        errors.append("Applications must be a dictionary")
        return errors

    if len(apps) == 0:
        errors.append("Application registry must contain at least one app")
        return errors

    # Validate each app definition
    for app_name, app_def in apps.items():
        if not isinstance(app_def, dict):
            errors.append(f"App '{app_name}' definition must be a dictionary")
            continue

        # Check cmd field
        if "cmd" in app_def:
            cmd = app_def["cmd"]
            if not isinstance(cmd, (list, tuple)):
                errors.append(f"App '{app_name}': 'cmd' must be a list or tuple")

        # Check flags field if present
        if "flags" in app_def:
            flags = app_def["flags"]
            if not isinstance(flags, dict):
                errors.append(f"App '{app_name}': 'flags' must be a dictionary")

        # Check wait_window field if present
        if "wait_window" in app_def:
            wait_window = app_def["wait_window"]
            if not isinstance(wait_window, int):
                errors.append(f"App '{app_name}': 'wait_window' must be an integer")
            elif wait_window <= 0:
                errors.append(f"App '{app_name}': 'wait_window' must be positive")

    return errors


def validate_config_file(file_path: Path) -> list[str]:
    """Load and validate a config file. Returns list of errors."""
    if not file_path.exists():
        return [f"File not found: {file_path}"]

    try:
        with open(file_path, "r") as f:
            config = yaml.safe_load(f)
            return validate_config(config if config else {})
    except yaml.YAMLError as e:
        return [f"Invalid YAML in {file_path}: {e}"]
    except Exception as e:
        return [f"Error reading {file_path}: {e}"]


def validate_apps_file(file_path: Path) -> list[str]:
    """Load and validate an apps file. Returns list of errors."""
    if not file_path.exists():
        return [f"File not found: {file_path}"]

    try:
        with open(file_path, "r") as f:
            apps = yaml.safe_load(f)
            return validate_apps(apps if apps else {})
    except yaml.YAMLError as e:
        return [f"Invalid YAML in {file_path}: {e}"]
    except Exception as e:
        return [f"Error reading {file_path}: {e}"]


def _validate_workspace_entry(prefix: str, ws_value: Any) -> list[str]:
    """Validate a single workspace entry (list of apps or dict with apps/monitor)."""
    errors = []
    if isinstance(ws_value, list):
        for i, item in enumerate(ws_value):
            if not isinstance(item, (str, dict)):
                errors.append(f"{prefix}[{i}]: must be a string or dict, got {type(item).__name__}")
    elif isinstance(ws_value, dict):
        if "apps" in ws_value:
            apps = ws_value["apps"]
            if not isinstance(apps, list):
                errors.append(f"{prefix}: 'apps' must be a list")
            else:
                for i, item in enumerate(apps):
                    if not isinstance(item, (str, dict)):
                        errors.append(f"{prefix}['apps'][{i}]: must be a string or dict")
        if "monitor" in ws_value:
            monitor = ws_value["monitor"]
            if not isinstance(monitor, str):
                errors.append(f"{prefix}: 'monitor' must be a string")
    else:
        errors.append(f"{prefix}: workspace entry must be a list or dict with 'apps'/'monitor' keys")
    return errors


def raise_if_invalid(errors: list[str], context: str = "") -> None:
    """Raise ValueError with all errors if any exist."""
    if errors:
        error_msg = f"Validation failed{context}:"
        for error in errors:
            error_msg += f"\n  - {error}"
        raise ValueError(error_msg)
