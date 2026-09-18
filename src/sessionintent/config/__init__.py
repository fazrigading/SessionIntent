"""
SessionIntent Configuration Package
Provides configuration loading, validation, and management.
"""

from .loader import load_config, load_apps, init_default_configs, load_yaml_file
from .migration import (
    CONFIG_VERSION,
    config_version,
    migrate_v1_to_v2,
    migration_notice,
    needs_migration,
)
from .validator import (
    validate_config,
    validate_apps,
    validate_config_file,
    validate_apps_file,
    raise_if_invalid,
)

__all__ = [
    # Loading
    "load_config",
    "load_apps",
    "init_default_configs",
    "load_yaml_file",
    # Migration
    "CONFIG_VERSION",
    "config_version",
    "migrate_v1_to_v2",
    "migration_notice",
    "needs_migration",
    # Validation
    "validate_config",
    "validate_apps",
    "validate_config_file",
    "validate_apps_file",
    "raise_if_invalid",
]
