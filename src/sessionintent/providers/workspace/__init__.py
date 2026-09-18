"""Workspace providers."""

from .ewmh import EwmhWorkspaceProvider
from .gnome import GnomeWorkspaceProvider
from .hyprland import HyprlandWorkspaceProvider
from .kde import KdeWorkspaceProvider
from .sway import SwayWorkspaceProvider
from .wlroots import WlrootsWorkspaceProvider

__all__ = [
    "EwmhWorkspaceProvider",
    "GnomeWorkspaceProvider",
    "HyprlandWorkspaceProvider",
    "KdeWorkspaceProvider",
    "SwayWorkspaceProvider",
    "WlrootsWorkspaceProvider",
]
