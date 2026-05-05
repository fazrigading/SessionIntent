"""
SessionIntent Plugins Package
Provides extensible plugin architecture.
"""

from .system import Plugin, PluginManager, get_plugin_manager

__all__ = [
    "Plugin",
    "PluginManager",
    "get_plugin_manager",
]