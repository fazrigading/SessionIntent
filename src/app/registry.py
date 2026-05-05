"""
SessionIntent App Registry
Loads and manages application definitions from config files.
"""

from __future__ import annotations

from typing import Any

from ..constants import APPS_PATH, SYSTEM_APPS_PATH
from ..config.loader import load_yaml_file as _load_yaml


class AppRegistry:
    """Registry for application definitions with support for layered loading."""

    def __init__(self):
        self._apps: dict[str, dict[str, Any]] = {}

    def load(self) -> None:
        """Load app definitions from all sources (system + user)."""
        self._apps = self._merge_app_sources()

    def _merge_app_sources(self) -> dict[str, dict[str, Any]]:
        """Merge app definitions from system and user sources."""
        bundled_apps = {}

        # Load system apps
        if SYSTEM_APPS_PATH.exists():
            bundled_apps = _load_yaml(SYSTEM_APPS_PATH)

        # Check current directory for dev purposes
        local_dev_path = SYSTEM_APPS_PATH.parent / "apps.yaml"
        if local_dev_path.exists():
            local_apps = _load_yaml(local_dev_path)
            bundled_apps.update(local_apps)

        # Load user apps (overrides bundled)
        user_apps = {}
        if APPS_PATH.exists():
            user_apps = _load_yaml(APPS_PATH)

        # Merge: bundled first, then user
        return {**bundled_apps, **user_apps}

    def get(self, app_key: str) -> dict[str, Any] | None:
        """Get app definition by key, or None if not found."""
        return self._apps.get(app_key)

    def get_or_default(self, app_key: str) -> dict[str, Any]:
        """Get app definition or create a minimal default."""
        return self._apps.get(app_key, {})

    def has(self, app_key: str) -> bool:
        """Check if app key exists in registry."""
        return app_key in self._apps

    def keys(self) -> list:
        """Return list of all app keys."""
        return list(self._apps.keys())

    def items(self) -> list:
        """Return list of (key, definition) tuples."""
        return list(self._apps.items())

    def __contains__(self, app_key: str) -> bool:
        """Support 'in' operator."""
        return app_key in self._apps

    def __getitem__(self, app_key: str) -> dict[str, Any]:
        """Support dict-style access."""
        return self._apps[app_key]

    def __len__(self) -> int:
        """Return number of apps in registry."""
        return len(self._apps)

    def __iter__(self):
        """Iterate over app keys."""
        return iter(self._apps)


# Singleton instance
_default_registry = None


def get_registry() -> AppRegistry:
    """Get the default app registry instance."""
    global _default_registry
    if _default_registry is None:
        _default_registry = AppRegistry()
        _default_registry.load()
    return _default_registry
