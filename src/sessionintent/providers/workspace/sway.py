"""
SessionIntent Sway Workspace Provider
Workspace management via swaymsg.
"""

from __future__ import annotations

import json
import subprocess
import time

from .ewmh import EwmhWorkspaceProvider


def _run(args: list[str], dev_mode: bool = False) -> str | None:
    """Run swaymsg and return stripped stdout, or None on failure."""
    if dev_mode:
        return None
    try:
        result = subprocess.run(
            args, capture_output=True, text=True, timeout=5, check=True
        )
        return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return None


def _workspaces(dev_mode: bool = False) -> list[dict]:
    """List Sway workspaces, or empty on failure."""
    out = _run(["swaymsg", "-t", "get_workspaces"], dev_mode=dev_mode)
    if not out:
        return []
    try:
        workspaces = json.loads(out)
        return workspaces if isinstance(workspaces, list) else []
    except json.JSONDecodeError:
        return []


class SwayWorkspaceProvider:
    """Sway workspace management via swaymsg."""

    def __init__(self, dev_mode: bool = False) -> None:
        self._dev_mode = dev_mode
        self._ewmh = EwmhWorkspaceProvider(dev_mode=dev_mode)

    def switch_workspace(self, num: int, monitor: str | None = None) -> bool:
        if self._dev_mode:
            monitor_str = f" on monitor {monitor}" if monitor else ""
            print(f"[DEV] Switching to workspace {num}{monitor_str}")
            return True
        result = _run(["swaymsg", "workspace", "number", str(num)])
        if result is None:
            return False
        try:
            return bool(json.loads(result)[0].get("success", False))
        except (json.JSONDecodeError, IndexError, KeyError, AttributeError):
            return True  # Command ran; sway only reports failures as non-zero.

    def get_current_workspace(self) -> int | None:
        if self._dev_mode:
            return 1
        for workspace in _workspaces():
            if workspace.get("focused"):
                try:
                    num = workspace.get("num")
                    if num is not None:
                        return int(num)
                except (ValueError, TypeError):
                    pass
        return None

    def get_workspace_count(self) -> int:
        if self._dev_mode:
            return 1
        return len(_workspaces()) or 1

    def wait_for_workspace(self, target: int, timeout: float = 2.0) -> bool:
        if self._dev_mode:
            return True
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.get_current_workspace() == target:
                return True
            time.sleep(0.1)
        return False

    def wait_for_window(
        self,
        app_pattern: str,
        target_workspace: int,
        timeout: float = 15.0,
    ) -> bool:
        return self._ewmh.wait_for_window(app_pattern, target_workspace, timeout)


__all__ = ["SwayWorkspaceProvider"]
