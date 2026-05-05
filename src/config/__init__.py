"""
SessionIntent Configuration Package
Provides configuration loading, validation, and management.
"""

from .loader import load_config, load_apps, init_default_configs, load_yaml_file
from .validator import (
    validate_config,
    validate_apps,
    validate_config_file,
    validate_apps_file,
    raise_if_invalid,
)
from .watcher import get_config_watcher, ConfigWatcher, PollingConfigWatcher

__all__ = [
    # Loading
    "load_config",
    "load_apps",
    "init_default_configs",
    "load_yaml_file",
    # Validation
    "validate_config",
    "validate_apps",
    "validate_config_file",
    "validate_apps_file",
    "raise_if_invalid",
    # Watching
    "get_config_watcher",
    "ConfigWatcher",
    "PollingConfigWatcher",
]
