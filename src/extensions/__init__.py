# SessionIntent Extensions Package
# Exports extension management functionality

"""
SessionIntent Extensions Package
Provides GNOME Shell extension management (enable/disable).
"""

from .manager import (
    resolve_extension_id,
    list_extensions,
    get_enabled_extensions,
    get_extension_info,
    enable_extension,
    disable_extension,
    apply_extensions,
    is_extension_installed,
    EXTENSION_REGISTRY,
)

__all__ = [
    "resolve_extension_id",
    "list_extensions",
    "get_enabled_extensions",
    "get_extension_info",
    "enable_extension",
    "disable_extension",
    "apply_extensions",
    "is_extension_installed",
    "EXTENSION_REGISTRY",
]
