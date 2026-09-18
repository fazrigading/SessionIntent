"""
SessionIntent Extensions Package
Compatibility re-exports; new code should use sessionintent.providers.
"""

from ..providers.extensions.gnome import (
    EXTENSION_REGISTRY,
    GnomeExtensionProvider,
    NullExtensionProvider,
    apply_extensions,
    disable_extension,
    enable_extension,
    get_enabled_extensions,
    get_extension_info,
    is_extension_installed,
    list_extensions,
    resolve_extension_id,
)

__all__ = [
    "EXTENSION_REGISTRY",
    "GnomeExtensionProvider",
    "NullExtensionProvider",
    "apply_extensions",
    "disable_extension",
    "enable_extension",
    "get_enabled_extensions",
    "get_extension_info",
    "is_extension_installed",
    "list_extensions",
    "resolve_extension_id",
]
