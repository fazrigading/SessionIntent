"""
SessionIntent Config Migration
Detect version: 1 configs, migrate them to version: 2 in memory,
and point users at the migration guide.
"""

from __future__ import annotations

import copy
from typing import Any

CONFIG_VERSION = 2

# Keys retired from the version: 2 schema (unwired features).
RETIRED_TOP_LEVEL_KEYS = ("time_schedules", "settings")
RETIRED_MODE_KEYS = ("schedule", "settings", "time_schedules")
RETIRED_MODE_HARDWARE_KEYS = ("battery_only",)


def config_version(config: dict[str, Any]) -> int:
    """
    Return the schema version of a config (1 when undeclared).

    Args:
        config: Loaded config dictionary

    Returns:
        2 for version: 2 configs, 1 otherwise
    """
    if not isinstance(config, dict):
        return 1
    version = config.get("version", 1)
    return version if version == CONFIG_VERSION else 1


def needs_migration(config: dict[str, Any]) -> bool:
    """True when the config is not a version: 2 config."""
    return config_version(config) != CONFIG_VERSION


def migrate_v1_to_v2(config: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """
    Migrate a version: 1 config to version: 2.

    Sets version: 2 and drops retired keys. Does not write to disk.

    Args:
        config: Loaded version: 1 config dictionary

    Returns:
        Tuple of (migrated config, stripped key paths for reporting)
    """
    migrated = copy.deepcopy(config) if isinstance(config, dict) else {}
    stripped: list[str] = []

    for key in RETIRED_TOP_LEVEL_KEYS:
        if key in migrated:
            del migrated[key]
            stripped.append(key)

    modes = migrated.get("modes")
    if isinstance(modes, dict):
        for mode_name, mode_cfg in modes.items():
            if not isinstance(mode_cfg, dict):
                continue
            for key in RETIRED_MODE_KEYS:
                if key in mode_cfg:
                    del mode_cfg[key]
                    stripped.append(f"modes.{mode_name}.{key}")
            hardware = mode_cfg.get("hardware")
            if isinstance(hardware, dict):
                for key in RETIRED_MODE_HARDWARE_KEYS:
                    if key in hardware:
                        del hardware[key]
                        stripped.append(f"modes.{mode_name}.hardware.{key}")

    migrated["version"] = CONFIG_VERSION
    return migrated, stripped


def migration_notice(stripped: list[str] | None = None) -> str:
    """
    Human-readable notice for a migrated version: 1 config.

    Args:
        stripped: Retired key paths dropped by the migration, if known
    """
    lines = [
        "Config migration: version: 1 config loaded as version: 2.",
        "Add 'version: 2' to config.yaml to silence this notice.",
        "See docs/MIGRATION.md for the flag-to-command table and schema changes.",
    ]
    if stripped:
        lines.append(f"Retired keys dropped: {', '.join(stripped)}.")
    return " ".join(lines)


__all__ = [
    "CONFIG_VERSION",
    "RETIRED_TOP_LEVEL_KEYS",
    "RETIRED_MODE_KEYS",
    "RETIRED_MODE_HARDWARE_KEYS",
    "config_version",
    "needs_migration",
    "migrate_v1_to_v2",
    "migration_notice",
]
