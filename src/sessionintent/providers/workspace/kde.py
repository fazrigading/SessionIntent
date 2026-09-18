"""
SessionIntent KDE Workspace Provider
KDE Plasma workspace management via qdbus.
"""

from __future__ import annotations

import subprocess
import time

from .ewmh import EwmhWorkspaceProvider


def _run(args: list[str], dev_mode: bool = False) -> str | None:
    """Run qdbus and return stripped stdout, or None on failure."""
    if dev_mode:
        return None
    try:
        result = subprocess.run(
            args, capture_output=True, text=True, timeout=5, check=True
        )
        return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return None


class KdeWorkspaceProvider:
    """KDE Plasma workspace management via qdbus org.kde.KWin."""

    def __init__(self, dev_mode: bool = False) -> None:
        self._dev_mode = dev_mode
        self._ewmh = EwmhWorkspaceProvider(dev_mode=dev_mode)

    def switch_workspace(self, num: int, monitor: str | None = None) -> bool:
        if self._dev_mode:
            monitor_str = f" on monitor {monitor}" if monitor else ""
            print(f"[DEV] Switching to workspace {num}{monitor_str}")
            return True
        return (
            _run(["qdbus", "org.kde.KWin", "/KWin", "setCurrentDesktop", str(num)])
            is not None
        )

    def get_current_workspace(self) -> int | None:
        if self._dev_mode:
            return 1
        out = _run(["qdbus", "org.kde.KWin", "/KWin", "currentDesktop"])
        if out is None:
            return None
        try:
            return int(out)
        except ValueError:
            return None

    def get_workspace_count(self) -> int:
        if self._dev_mode:
            return 1
        out = _run(["qdbus", "org.kde.KWin", "/KWin", "numberOfDesktops"])
        if out is None:
            return 1
        try:
            return int(out)
        except ValueError:
            return 1

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


__all__ = ["KdeWorkspaceProvider"]
