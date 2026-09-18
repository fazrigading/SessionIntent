"""
SessionIntent Plugin System
Provides extensible plugin architecture for SessionIntent.
"""

from __future__ import annotations

import importlib.util
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from ..constants import CONFIG_DIR
from ..session.log import info, warning, error


PLUGIN_DIR = CONFIG_DIR / "plugins"


class Plugin:
    """Base class for SessionIntent plugins."""

    name: str = "base"
    version: str = "1.0.0"

    def on_load(self) -> bool:
        """Called when plugin is loaded. Return False to disable plugin."""
        return True

    def on_unload(self) -> None:
        """Called when plugin is unloaded."""
        pass

    def on_mode_apply(self, mode_name: str, config: dict[str, Any]) -> dict[str, Any]:
        """Called before mode is applied. May modify config."""
        return config

    def on_mode_applied(self, mode_name: str) -> None:
        """Called after mode is applied."""
        pass


class PluginManager:
    """Manages plugin lifecycle."""

    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}
        self._hooks: dict[str, list[Callable]] = {
            "on_mode_apply": [],
            "on_mode_applied": [],
        }

    def discover_plugins(self) -> None:
        """Discover and load plugins from plugin directory."""
        if not PLUGIN_DIR.exists():
            PLUGIN_DIR.mkdir(parents=True, exist_ok=True)
            return

        for file_path in PLUGIN_DIR.glob("*.py"):
            if file_path.stem.startswith("_"):
                continue
            self._load_plugin_file(file_path)

    def _load_plugin_file(self, file_path: Path) -> None:
        """Load a plugin from file."""
        spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
        if spec is None or spec.loader is None:
            return

        module = importlib.util.module_from_spec(spec)
        sys.modules[file_path.stem] = module
        spec.loader.exec_module(module)

        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, Plugin)
                and attr is not Plugin
            ):
                self.load_plugin(attr())

    def load_plugin(self, plugin: Plugin) -> bool:
        """Load a plugin instance."""
        if not plugin.on_load():
            warning(f"Plugin {plugin.name} refused to load")
            return False

        self._plugins[plugin.name] = plugin
        info(f"Loaded plugin: {plugin.name}")
        return True

    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin by name."""
        plugin = self._plugins.get(plugin_name)
        if not plugin:
            return False

        plugin.on_unload()
        del self._plugins[plugin_name]
        info(f"Unloaded plugin: {plugin_name}")
        return True

    def get_plugin(self, plugin_name: str) -> Plugin | None:
        """Get a plugin by name."""
        return self._plugins.get(plugin_name)

    def get_plugins(self) -> dict[str, Plugin]:
        """Get all loaded plugins."""
        return self._plugins.copy()

    def register_hook(self, hook_name: str, callback: Callable) -> None:
        """Register a callback for a hook."""
        if hook_name in self._hooks:
            self._hooks[hook_name].append(callback)

    def trigger_hook(self, hook_name: str, *args: Any, **kwargs: Any) -> list[Any]:
        """Trigger all callbacks for a hook."""
        results: list[Any] = []
        if hook_name in self._hooks:
            for callback in self._hooks[hook_name]:
                try:
                    results.append(callback(*args, **kwargs))
                except Exception as e:
                    error(f"Hook {hook_name} failed: {e}")
        return results


_manager: PluginManager | None = None


def get_plugin_manager() -> PluginManager:
    """Get global plugin manager instance."""
    global _manager  # noqa: PLW0603

    if _manager is None:
        _manager = PluginManager()
        _manager.discover_plugins()

    return _manager


__all__ = [
    "Plugin",
    "PluginManager",
    "get_plugin_manager",
]