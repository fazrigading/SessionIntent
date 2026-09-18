"""
SessionIntent Constants Package
Provides centralized access to all configuration constants.
"""

from .paths import (
    CONFIG_DIR,
    SYSTEM_CONFIG_DIR,
    STATE_DIR,
    CONFIG_PATH,
    SYSTEM_CONFIG_PATH,
    APPS_PATH,
    SYSTEM_APPS_PATH,
    STATE_FILE,
    AC_PATH,
    LOG_DIR,
    LOG_FILE,
)

from .defaults import DEFAULT_APPS, DEFAULT_CONFIG

__all__ = [
    # Paths
    "CONFIG_DIR",
    "SYSTEM_CONFIG_DIR",
    "STATE_DIR",
    "CONFIG_PATH",
    "SYSTEM_CONFIG_PATH",
    "APPS_PATH",
    "SYSTEM_APPS_PATH",
    "STATE_FILE",
    "AC_PATH",
    "LOG_DIR",
    "LOG_FILE",
    # Defaults
    "DEFAULT_APPS",
    "DEFAULT_CONFIG",
]
