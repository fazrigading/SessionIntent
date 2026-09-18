"""
SessionIntent Session Manager
Main orchestrator that coordinates configuration, hardware, UI, and app launching.
"""

from __future__ import annotations

import os
import time
from typing import Any

from ..constants import CONFIG_PATH, STATE_DIR
from ..config import (
    load_config,
    load_apps,
    init_default_configs,
    needs_migration,
    migrate_v1_to_v2,
    migration_notice,
)
from ..config.validator import raise_if_invalid, validate_config
from ..plugins import PluginManager, get_plugin_manager
from .notify import notify_error, notify_mode_change
from ..hardware import is_on_ac
from ..providers import DisplayProvider, ExtensionProvider, WorkspaceProvider, get_providers
from ..app import launch_app
from ..session.state import save_state
from .snapshot import save_snapshot


class SessionManager:
    """Main session manager class that orchestrates all session operations."""

    def __init__(
        self,
        dev_mode: bool = False,
        config_path: str | None = None,
        backend: str | None = None,
    ):
        """
        Initialize the session manager.

        Args:
            dev_mode: If True, print commands instead of executing
            config_path: Optional path to custom config file
            backend: Optional workspace backend override
                (gnome, ewmh, kde, hyprland, sway, wlroots).
                Auto-detected from the desktop environment when None.
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

        # Resolve desktop providers (detection + factory).
        self._workspace: WorkspaceProvider
        self._display: DisplayProvider
        self._extensions: ExtensionProvider
        self._workspace, self._display, self._extensions = get_providers(
            dev_mode=dev_mode, backend=backend
        )

        # Initialize state directory (unless in dev mode)
        if not self.dev_mode:
            STATE_DIR.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> None:
        """Load, migrate, validate, and store configuration and app registry."""
        raw = load_config(str(self.config_path))
        if needs_migration(raw):
            migrated, stripped = migrate_v1_to_v2(raw)
            print(migration_notice(stripped))
            raw = migrated
        raise_if_invalid(validate_config(raw), f" in {self.config_path}")
        self.config = raw
        self.apps = load_apps()

    def init_config(self) -> None:
        """Initialize default configuration files and ensure the workspace extension is installed."""
        init_default_configs()
        ok, msg = self._extensions.ensure()
        if not ok:
            print(f"Warning: {msg}")
        elif not self.dev_mode:
            print(f"Workspace extension: {msg}")
        # Reload config after initialization
        try:
            self._load_config()
        except (ValueError, IOError):
            pass

    def get_available_modes(self) -> dict[str, Any]:
        """Get modes available based on current hardware state."""
        all_modes = self.config.get("modes", {})
        if not is_on_ac():
            disabled = (
                self.config.get("hardware_profiles", {})
                .get("battery", {})
                .get("disable_modes", [])
            )
            return {k: v for k, v in all_modes.items() if k not in disabled}
        return all_modes

    def select_mode(self) -> str | None:
        """Display UI and return selected mode key."""
        return self._display.select_mode(self.get_available_modes())

    def apply_mode(self, mode_name: str) -> None:
        """
        Apply a specific session mode.

        Args:
            mode_name: Key of the mode to apply
        """
        mode_cfg = self.config.get("modes", {}).get(mode_name, {})

        if not mode_cfg:
            print(f"Mode '{mode_name}' not found.")
            notify_error(f"Mode '{mode_name}' not found.", self.dev_mode)
            return

        print(f"Applying mode: {mode_name}")
        mode_cfg = self._run_apply_hooks(mode_name, mode_cfg)

        # Apply extensions first
        extensions_config = mode_cfg.get("extensions", {})
        if extensions_config:
            print("Managing GNOME extensions...")
            ext_messages = self._extensions.apply(extensions_config)
            for msg in ext_messages:
                print(f"  {msg}")

        # Apply workspaces and apps
        workspaces = mode_cfg.get("workspaces", {})

        for ws_num_str in sorted(workspaces.keys(), key=int):
            ws_num = int(ws_num_str)
            ws_value = workspaces[ws_num_str]

            if isinstance(ws_value, dict):
                apps_in_ws = ws_value.get("apps", [])
                monitor = ws_value.get("monitor")
            else:
                apps_in_ws = ws_value
                monitor = None

            # Check current workspace, skip if already there
            current_ws = self._workspace.get_current_workspace()
            if current_ws == ws_num:
                print(f"  Already on workspace {ws_num}, launching apps...")
            else:
                ok = self._workspace.switch_workspace(ws_num, monitor=monitor)
                if not ok:
                    print(
                        f"  Warning: workspace switch to {ws_num} failed. "
                        "Ensure SessionIntent extension is installed: "
                        "sessionintent init"
                    )
                else:
                    monitor_str = f" (monitor: {monitor})" if monitor else ""
                    print(f"  Switched to workspace {ws_num}{monitor_str}")
                    # Wait for workspace switch animation to complete
                    time.sleep(4)

            for app_entry in apps_in_ws:
                app_key, params = self._parse_app_entry(app_entry, mode_cfg)
                print(f"  Launching {app_key}...")
                launch_app(app_key, params, self.apps, self.dev_mode)
                print(f"  {app_key} launched.")

                app_def = self.apps.get(app_key, {})
                check_pattern = app_def.get("check", app_key)
                global_wait = self.config.get("defaults", {}).get("wait_window", 15)
                wait_timeout = app_def.get("wait_window", global_wait)

                if check_pattern is not False:
                    self._workspace.wait_for_window(
                        check_pattern, ws_num, wait_timeout
                    )
                else:
                    time.sleep(4)

        # Save state (unless in dev mode)
        save_state(mode_name, self.dev_mode)

        # Save window snapshot
        save_snapshot(mode_name, self.dev_mode)

        notify_mode_change(
            mode_name, mode_cfg.get("label", mode_name), self.dev_mode
        )
        self._run_applied_hooks(mode_name)

    def _plugin_manager(self) -> PluginManager | None:
        """Plugin manager, or None in dev mode (no discovery side effects)."""
        if self.dev_mode:
            return None
        try:
            return get_plugin_manager()
        except Exception as e:
            print(f"Warning: plugin discovery failed: {e}")
            return None

    def _run_apply_hooks(
        self, mode_name: str, mode_cfg: dict[str, Any]
    ) -> dict[str, Any]:
        """Let plugins adjust the mode config before it is applied."""
        manager = self._plugin_manager()
        if manager is None:
            return mode_cfg
        for plugin in manager.get_plugins().values():
            try:
                result = plugin.on_mode_apply(mode_name, mode_cfg)
                if isinstance(result, dict):
                    mode_cfg = result
            except Exception as e:
                print(f"Warning: plugin '{plugin.name}' on_mode_apply failed: {e}")
        manager.trigger_hook("on_mode_apply", mode_name, mode_cfg)
        return mode_cfg

    def _run_applied_hooks(self, mode_name: str) -> None:
        """Notify plugins that a mode was applied."""
        manager = self._plugin_manager()
        if manager is None:
            return
        for plugin in manager.get_plugins().values():
            try:
                plugin.on_mode_applied(mode_name)
            except Exception as e:
                print(f"Warning: plugin '{plugin.name}' on_mode_applied failed: {e}")
        manager.trigger_hook("on_mode_applied", mode_name)

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
        if self.dev_mode:
            print("[DEV] Panic: Would clear state.")
            return

        from ..session.state import clear_state

        clear_state(self.dev_mode)
        print("Panic: State cleared.")

    def quit(self) -> None:
        """Gracefully close managed applications (SIGTERM)."""
        if self.dev_mode:
            print("[DEV] Quit: Would gracefully close managed apps.")
            return

        from ..session.state import load_state

        current_mode = load_state()

        if not current_mode:
            print("Quit: No active mode to quit from.")
            return

        mode_cfg = self.config.get("modes", {}).get(current_mode, {})
        apps_to_close = self._get_managed_apps(mode_cfg)

        if not apps_to_close:
            print("Quit: No managed applications to close.")
            return

        print(f"Quit: Closing {len(apps_to_close)} application(s)...")
        self._close_apps(apps_to_close, graceful=True)

        from ..session.state import clear_state

        clear_state(self.dev_mode)
        print("Quit: Done.")

    def clear(self) -> None:
        """Clear state files only (no app management)."""
        if self.dev_mode:
            print("[DEV] Clear: Would clear state files only.")
            return

        from ..session.state import clear_state

        clear_state(self.dev_mode)
        print("Clear: State files cleared.")

    def _get_managed_apps(self, mode_cfg: dict[str, Any]) -> list[str]:
        """Get list of app keys managed by the current mode."""
        apps = []
        workspaces = mode_cfg.get("workspaces", {})
        for ws_apps in workspaces.values():
            for app_entry in ws_apps:
                if isinstance(app_entry, str):
                    apps.append(app_entry)
                else:
                    apps.append(list(app_entry.keys())[0])
        return apps

    def _close_apps(self, app_keys: list[str], graceful: bool = True) -> None:
        """Close applications by their keys."""
        import subprocess

        for app_key in app_keys:
            app_def = self.apps.get(app_key, {})
            check_pattern = app_def.get("check", app_key)

            if check_pattern is False:
                continue

            try:
                if graceful:
                    subprocess.run(
                        ["pkill", "-TERM", "-f", check_pattern],
                        capture_output=True,
                    )
                else:
                    subprocess.run(
                        ["pkill", "-KILL", "-f", check_pattern],
                        capture_output=True,
                    )
            except subprocess.CalledProcessError:
                pass

    def status(self) -> None:
        """Show current session status."""
        from ..session.state import load_state

        current_mode = load_state()
        power_state = "AC" if is_on_ac() else "Battery"

        print("=== SessionIntent Status ===")
        print(f"Current Mode: {current_mode or 'None'}")
        print(f"Power State: {power_state}")
        print(f"Dev Mode: {self.dev_mode}")
        print(f"Config Path: {self.config_path}")

    def list_modes(self) -> None:
        """List all available modes."""
        modes = self.config.get("modes", {})
        hardware_profile = "plugged" if is_on_ac() else "battery"
        profile_config = self.config.get("hardware_profiles", {}).get(
            hardware_profile, {}
        )
        disabled_modes = profile_config.get("disable_modes", [])

        print("=== Available Modes ===")
        if not modes:
            print("  No modes defined.")
            return

        for mode_key, mode_data in modes.items():
            label = mode_data.get("label", mode_key)
            if mode_key in disabled_modes:
                print(f"  {mode_key} ({label}) - [Disabled on {hardware_profile}]")
            else:
                print(f"  {mode_key} ({label})")

    def kill(self) -> None:
        """Force kill managed applications (SIGKILL)."""
        if self.dev_mode:
            print("[DEV] Kill: Would force kill managed apps.")
            return

        from ..session.state import load_state

        current_mode = load_state()

        if not current_mode:
            print("Kill: No active mode to kill apps from.")
            return

        mode_cfg = self.config.get("modes", {}).get(current_mode, {})
        apps_to_kill = self._get_managed_apps(mode_cfg)

        if not apps_to_kill:
            print("Kill: No managed applications to kill.")
            return

        print(f"Kill: Force killing {len(apps_to_kill)} application(s)...")
        self._close_apps(apps_to_kill, graceful=False)
        print("Kill: Done.")

    def reload(self) -> None:
        """Reload configuration files."""
        if self.dev_mode:
            print("[DEV] Reload: Would reload configuration.")
            return

        try:
            self._load_config()
            print("Reload: Configuration reloaded.")
        except (ValueError, IOError) as e:
            print(f"Reload: Failed to reload config: {e}")

    def suspend(self) -> None:
        """Suspend session (pause mode switching)."""
        if self.dev_mode:
            print("[DEV] Suspend: Would suspend session.")
            return

        from ..session.state import load_state, save_state

        current_mode = load_state()
        if not current_mode:
            print("Suspend: No active mode to suspend.")
            return

        save_state(f"suspend:{current_mode}", self.dev_mode)
        print("Suspend: Session suspended. Use quit to resume and close apps.")

    def restore(self) -> None:
        """Restore window positions from snapshot."""
        if self.dev_mode:
            print("[DEV] Would restore window snapshot.")
            return

        from ..session.state import load_state

        current_mode = load_state()

        if not current_mode:
            print("Restore: No active mode to restore.")
            return

        from .snapshot import restore_snapshot

        restore_snapshot(current_mode, self.dev_mode)
        print("Restore: Window positions restored.")


# convenience imports for direct use
