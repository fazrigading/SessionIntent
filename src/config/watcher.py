"""
SessionIntent Config Watcher
Watches configuration files for changes and triggers reloads.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Callable

try:
    from watchdog.observers import Observer  # type: ignore[import-not-found]
    from watchdog.events import FileSystemEventHandler  # type: ignore[import-not-found]

    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False

from ..constants import CONFIG_PATH, APPS_PATH, SYSTEM_CONFIG_PATH, SYSTEM_APPS_PATH


class ConfigFileHandler(FileSystemEventHandler if HAS_WATCHDOG else object):  # type: ignore[misc]
    """Handler for config file changes."""

    def __init__(
        self,
        on_config_change: Callable[[], None] | None = None,
        on_apps_change: Callable[[], None] | None = None,
    ) -> None:
        self.on_config_change = on_config_change
        self.on_apps_change = on_apps_change

    def on_modified(self, event: Any) -> None:
        if not event.is_directory:
            path = Path(event.src_path)
            if path == CONFIG_PATH or path == SYSTEM_CONFIG_PATH:
                if self.on_config_change:
                    self.on_config_change()
            elif path == APPS_PATH or path == SYSTEM_APPS_PATH:
                if self.on_apps_change:
                    self.on_apps_change()


class ConfigWatcher:
    """Watches configuration files for changes."""

    def __init__(self) -> None:
        if not HAS_WATCHDOG:
            raise ImportError("watchdog library is required for config hot reload")

        self._observer: Observer | None = None
        self._on_reload: Callable[[], None] | None = None

    def start(
        self,
        on_config_change: Callable[[], None] | None = None,
        on_apps_change: Callable[[], None] | None = None,
    ) -> None:
        """Start watching config files."""
        if not HAS_WATCHDOG:
            return

        handler = ConfigFileHandler(on_config_change, on_apps_change)
        self._on_reload = on_config_change

        self._observer = Observer()
        self._observer.start()

        dirs_to_watch: set[Path] = set()

        for path in (CONFIG_PATH, APPS_PATH, SYSTEM_CONFIG_PATH, SYSTEM_APPS_PATH):
            if path and path.exists():
                dirs_to_watch.add(path.parent)

        for dir_path in dirs_to_watch:
            self._observer.schedule(handler, str(dir_path), recursive=False)

    def stop(self) -> None:
        """Stop watching config files."""
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None

    def is_watching(self) -> bool:
        """Check if watcher is active."""
        return self._observer is not None and self._observer.is_alive()


class PollingConfigWatcher:
    """Fallback config watcher using polling (when watchdog not available)."""

    def __init__(
        self,
        poll_interval: float = 1.0,
    ) -> None:
        self._poll_interval = poll_interval
        self._running = False
        self._thread: Any = None
        self._on_config_change: Callable[[], None] | None = None
        self._on_apps_change: Callable[[], None] | None = None
        self._last_mtimes: dict[Path, float] = {}

    def start(
        self,
        on_config_change: Callable[[], None] | None = None,
        on_apps_change: Callable[[], None] | None = None,
    ) -> None:
        """Start polling config files."""
        self._on_config_change = on_config_change
        self._on_apps_change = on_apps_change
        self._running = True
        self._update_mtimes()

        import threading

        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop polling config files."""
        self._running = False
        if self._thread:
            self._thread.join()
            self._thread = None

    def is_watching(self) -> bool:
        """Check if watcher is active."""
        return self._running

    def _update_mtimes(self) -> None:
        """Update modification times."""
        for path in (CONFIG_PATH, APPS_PATH):
            try:
                if path.exists():
                    self._last_mtimes[path] = path.stat().st_mtime
            except OSError:
                pass

    def _poll_loop(self) -> None:
        """Poll loop for checking file changes."""
        while self._running:
            time.sleep(self._poll_interval)

            for path in (CONFIG_PATH, APPS_PATH):
                try:
                    if path.exists():
                        current_mtime = path.stat().st_mtime
                        last_mtime = self._last_mtimes.get(path, 0)

                        if current_mtime > last_mtime:
                            self._last_mtimes[path] = current_mtime

                            if path == CONFIG_PATH and self._on_config_change:
                                self._on_config_change()
                            elif path == APPS_PATH and self._on_apps_change:
                                self._on_apps_change()
                except OSError:
                    pass


def get_config_watcher() -> ConfigWatcher | PollingConfigWatcher:
    """Get a config watcher instance."""
    if HAS_WATCHDOG:
        return ConfigWatcher()
    return PollingConfigWatcher()


__all__ = [
    "ConfigWatcher",
    "PollingConfigWatcher",
    "get_config_watcher",
]