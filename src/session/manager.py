"""
SessionIntent Session Manager
Main orchestrator that coordinates configuration, hardware, UI, and app launching.
"""

from __future__ import annotations

import os
from typing import Any

from ..constants import CONFIG_PATH, STATE_DIR
from ..config import load_config, load_apps, init_default_configs
from ..hardware import is_on_ac
from ..ui import select_mode, get_available_modes
from ..workspace import switch_workspace
from ..app import launch_app, get_registry
from ..session.state import save_state
from ..extensions import apply_extensions


class SessionManager:
    """Main session manager class that orchestrates all session operations."""

    def __init__(self, dev_mode: bool = False, config_path: str | None = None):
        """
        Initialize the session manager.

        Args:
            dev_mode: If True, print commands instead of executing
            config_path: Optional path to custom config file
        """
        self.config: dict[str, Any] = {}
        self.apps: dict[str, dict[str, Any]] = {}
        self.dev_mode = dev_mode
        self.config_path = CONFIG_PATH if config_path is None else config_path

        # Load configuration and apps (may fail if config doesn't exist)
        try:
            self._load_config()
        except (ValueError, IOError) as e:
            # If config is invalid or missing, use empty config
            print(f"Warning: Could not load config: {e}")
            self.config = {}

        # Initialize state directory (unless in dev mode)
        if not self.dev_mode:
            STATE_DIR.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> None:
        """Load configuration and app registry."""
        self.config = load_config(str(self.config_path))
        self.apps = load_apps()

    def init_config(self) -> None:
        """Initialize default configuration files if they don't exist."""
        init_default_configs()
        # Reload config after initialization
        try:
            self._load_config()
        except (ValueError, IOError):
            pass

    def get_available_modes(self) -> dict[str, Any]:
        """Get modes available based on current hardware state."""
        return get_available_modes(self.config)

    def select_mode(self) -> str | None:
        """Display UI and return selected mode key."""
        return select_mode(self.config)

    def apply_mode(self, mode_name: str) -> None:
        """
        Apply a specific session mode.

        Args:
            mode_name: Key of the mode to apply
        """
        mode_cfg = self.config.get("modes", {}).get(mode_name, {})

        if not mode_cfg:
            print(f"Mode '{mode_name}' not found.")
            return

        print(f"Applying mode: {mode_name}")

        # Apply extensions first
        extensions_config = mode_cfg.get("extensions", {})
        if extensions_config:
            print("Managing GNOME extensions...")
            ext_messages = apply_extensions(extensions_config, self.dev_mode)
            for msg in ext_messages:
                print(f"  - {msg}")

        # Apply workspaces and apps
        workspaces = mode_cfg.get("workspaces", {})

        for ws_num_str in sorted(workspaces.keys(), key=int):
            ws_num = int(ws_num_str)
            apps_in_ws = workspaces[ws_num_str]

            switch_workspace(ws_num, self.dev_mode)

            for app_entry in apps_in_ws:
                app_key, params = self._parse_app_entry(app_entry, mode_cfg)
                launch_app(app_key, params, self.apps, self.dev_mode)

        # Save state (unless in dev mode)
        save_state(mode_name, self.dev_mode)

    def _parse_app_entry(self, app_entry, mode_cfg: dict[str, Any]) -> tuple:
        """
        Parse an app entry from workspace configuration.

        Args:
            app_entry: App definition (string or dict)
            mode_cfg: Mode configuration

        Returns:
            Tuple of (app_key, params_dict)
        """
        if isinstance(app_entry, str):
            return app_entry, {}

        # App entry is a dict with app key as first key
        app_key = list(app_entry.keys())[0]
        val = app_entry[app_key]

        if isinstance(val, dict):
            local_params = val
        else:
            app_def = self.apps.get(app_key, {})
            primary = app_def.get("primary_param", "value")
            local_params = {primary: val}

        # Merge with mode-level params
        mode_level_params = mode_cfg.get(app_key, {})
        if not isinstance(mode_level_params, dict):
            mode_level_params = {}

        # Final params with user path expansion
        final_params = {**mode_level_params, **local_params}
        final_params = {
            k: (os.path.expanduser(v) if isinstance(v, str) else v)
            for k, v in final_params.items()
        }

        return app_key, final_params

    def panic(self) -> None:
        """Clear current session state without killing processes."""
        import os

        if self.dev_mode:
            print("[DEV] Panic reset: Would clear state.")
            return

        if STATE_FILE.exists():
            try:
                STATE_FILE.unlink()
            except (IOError, OSError):
                pass

        print("Panic reset: State cleared.")


# convenience imports for direct use
from ..constants import CONFIG_DIR, STATE_DIR, STATE_FILE, AC_PATH
