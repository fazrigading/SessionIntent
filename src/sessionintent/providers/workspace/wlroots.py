"""
SessionIntent Generic wlroots Workspace Provider
Best-effort chain for wlroots compositors (River, Labwc, etc.):
Hyprland tooling first, then Sway, then generic EWMH.
"""

from __future__ import annotations

import shutil

from ..base import WorkspaceProvider
from .ewmh import EwmhWorkspaceProvider
from .hyprland import HyprlandWorkspaceProvider
from .sway import SwayWorkspaceProvider


class WlrootsWorkspaceProvider:
    """Delegate to the first available compositor tooling."""

    def __init__(self, dev_mode: bool = False) -> None:
        self._dev_mode = dev_mode
        self._inner: WorkspaceProvider
        if shutil.which("hyprctl"):
            self._inner = HyprlandWorkspaceProvider(dev_mode=dev_mode)
        elif shutil.which("swaymsg"):
            self._inner = SwayWorkspaceProvider(dev_mode=dev_mode)
        else:
            self._inner = EwmhWorkspaceProvider(dev_mode=dev_mode)

    def switch_workspace(self, num: int, monitor: str | None = None) -> bool:
        return self._inner.switch_workspace(num, monitor=monitor)

    def get_current_workspace(self) -> int | None:
        return self._inner.get_current_workspace()

    def get_workspace_count(self) -> int:
        return self._inner.get_workspace_count()

    def wait_for_workspace(self, target: int, timeout: float = 2.0) -> bool:
        return self._inner.wait_for_workspace(target, timeout)

    def wait_for_window(
        self,
        app_pattern: str,
        target_workspace: int,
        timeout: float = 15.0,
    ) -> bool:
        return self._inner.wait_for_window(app_pattern, target_workspace, timeout)


__all__ = ["WlrootsWorkspaceProvider"]
