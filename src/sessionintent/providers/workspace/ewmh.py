"""
SessionIntent EWMH Workspace Provider
Generic X11 fallback via wmctrl and xdotool.
"""

from __future__ import annotations

import subprocess
import time


def _run(cmd: list[str], dev_mode: bool = False) -> subprocess.CompletedProcess[str] | None:
    """Run a command, returning None on missing tool or failure."""
    if dev_mode:
        return None
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=5)
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return None


class EwmhWorkspaceProvider:
    """Generic EWMH workspace management via wmctrl/xdotool."""

    def __init__(self, dev_mode: bool = False) -> None:
        self._dev_mode = dev_mode

    def switch_workspace(self, num: int, monitor: str | None = None) -> bool:
        if self._dev_mode:
            monitor_str = f" on monitor {monitor}" if monitor else ""
            print(f"[DEV] Switching to workspace {num}{monitor_str}")
            return True
        result = _run(["wmctrl", "-s", str(num - 1)])
        return result is not None and result.returncode == 0

    def get_current_workspace(self) -> int | None:
        if self._dev_mode:
            return 1
        result = _run(["wmctrl", "-d"])
        if result is None or result.returncode != 0:
            return None
        for line in result.stdout.strip().split("\n"):
            parts = line.split()
            if len(parts) >= 2 and parts[1] == "*":
                try:
                    return int(parts[0]) + 1  # 1-indexed
                except ValueError:
                    pass
        return None

    def get_workspace_count(self) -> int:
        if self._dev_mode:
            return 1
        result = _run(["wmctrl", "-d"])
        if result is None or result.returncode != 0:
            return 1
        return len([line for line in result.stdout.strip().split("\n") if line])

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
        """
        Wait for an app window to appear on the target workspace.

        Args:
            app_pattern: Window class pattern to search for (passed to xdotool)
            target_workspace: 1-indexed workspace number to wait for
            timeout: Maximum seconds to wait (default 15s)

        Returns:
            True if window found on target workspace, False if timeout
        """
        if self._dev_mode:
            return True

        target_idx = target_workspace - 1
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            try:
                result = subprocess.run(
                    ["xdotool", "search", "--class", app_pattern],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                if result.returncode == 0:
                    window_ids = result.stdout.strip().split("\n")
                    for wid in window_ids:
                        if not wid:
                            continue
                        try:
                            desk_result = subprocess.run(
                                ["xdotool", "getwindowenv", wid, "_NET_WM_DESKTOP"],
                                capture_output=True,
                                text=True,
                                timeout=1,
                            )
                            if desk_result.returncode == 0:
                                try:
                                    ws_index = int(desk_result.stdout.strip())
                                    if ws_index == target_idx:
                                        return True
                                except ValueError:
                                    pass
                        except subprocess.TimeoutExpired:
                            pass
            except FileNotFoundError:
                return False
            except (subprocess.SubprocessError, OSError):
                pass

            time.sleep(0.5)

        return False


__all__ = ["EwmhWorkspaceProvider", "wait_for_window"]


def wait_for_window(
    app_pattern: str,
    target_workspace: int,
    timeout: float = 15.0,
    dev_mode: bool = False,
) -> bool:
    """Wait for an app window on the target workspace (see provider method)."""
    return EwmhWorkspaceProvider(dev_mode=dev_mode).wait_for_window(
        app_pattern, target_workspace, timeout
    )
