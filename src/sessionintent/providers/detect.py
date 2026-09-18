"""
SessionIntent Desktop Detection
Detect the desktop environment and select providers via a factory.
"""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field

from .base import DisplayProvider, ExtensionProvider, ProviderError, WorkspaceProvider


@dataclass
class DesktopProfile:
    """Detected desktop environment."""

    session_type: str  # wayland, x11, tty, unknown
    desktop: str  # gnome, kde, hyprland, sway, i3, unknown
    wm_type: str  # mutter, kwin, hyprland, sway, i3, unknown
    capabilities: set[str] = field(default_factory=set)
    tool_availability: dict[str, bool] = field(default_factory=dict)


TOOL_REQUIREMENTS = (
    "gdbus",
    "qdbus",
    "hyprctl",
    "swaymsg",
    "wmctrl",
    "xdotool",
    "wofi",
    "rofi",
)

_WM_TYPES = {
    "gnome": "mutter",
    "plasma": "kwin",
    "kde": "kwin",
    "hyprland": "hyprland",
    "sway": "sway",
    "i3": "i3",
    "wlroots": "wlroots",
}

BACKENDS = ("gnome", "ewmh", "kde", "hyprland", "sway", "wlroots")


def detect_desktop(env: dict[str, str] | None = None) -> DesktopProfile:
    """
    Detect the current desktop environment.

    Args:
        env: Environment mapping to read (defaults to os.environ).
            Accepts an explicit dict for testability.

    Returns:
        DesktopProfile with type, desktop, wm, capabilities, and tools.
    """
    env = env if env is not None else dict(os.environ)

    session_type = env.get("XDG_SESSION_TYPE", "unknown").lower()
    desktop = env.get("DESKTOP_SESSION", "unknown").lower()

    # Socket/instance signatures override the generic session name.
    if env.get("HYPRLAND_INSTANCE_SIGNATURE"):
        desktop = "hyprland"
    elif env.get("SWAYSOCK"):
        desktop = "sway"
    elif env.get("KDE_FULL_SESSION"):
        desktop = "kde"
    elif (
        session_type == "wayland"
        and desktop == "unknown"
        and env.get("WAYLAND_DISPLAY")
    ):
        desktop = "wlroots"

    tools = {tool: shutil.which(tool) is not None for tool in TOOL_REQUIREMENTS}

    capabilities: set[str] = set()
    if desktop in ("gnome", "unknown"):
        capabilities.update({"workspace", "extensions"})
    elif desktop == "kde":
        capabilities.update({"workspace", "extensions"})
    elif tools.get("wmctrl") or tools.get("xdotool"):
        capabilities.add("workspace")
    if tools.get("wofi") or tools.get("rofi"):
        capabilities.add("graphical_selector")

    return DesktopProfile(
        session_type=session_type,
        desktop=desktop,
        wm_type=_WM_TYPES.get(desktop, "unknown"),
        capabilities=capabilities,
        tool_availability=tools,
    )


def get_providers(
    profile: DesktopProfile | None = None,
    dev_mode: bool = False,
    backend: str | None = None,
) -> tuple[WorkspaceProvider, DisplayProvider, ExtensionProvider]:
    """
    Select workspace, display, and extension providers for a profile.

    Args:
        profile: Detected profile (auto-detected when None).
        dev_mode: Passed through to providers (no real calls).
        backend: Manual override, one of "gnome" or "ewmh".

    Returns:
        Tuple of (workspace, display, extensions) providers.

    Raises:
        ProviderError: If the backend name is unknown.
    """
    from .display.rofi import RofiDisplayProvider
    from .display.tui import TuiDisplayProvider
    from .extensions.gnome import GnomeExtensionProvider, NullExtensionProvider
    from .extensions.kde import KdeExtensionProvider
    from .workspace.ewmh import EwmhWorkspaceProvider
    from .workspace.gnome import GnomeWorkspaceProvider
    from .workspace.hyprland import HyprlandWorkspaceProvider
    from .workspace.kde import KdeWorkspaceProvider
    from .workspace.sway import SwayWorkspaceProvider
    from .workspace.wlroots import WlrootsWorkspaceProvider

    profile = profile if profile is not None else detect_desktop()

    desktop = (backend or profile.desktop or "unknown").lower()
    if backend is not None and desktop not in BACKENDS:
        raise ProviderError(
            f"Unknown backend: {backend!r} (expected one of {', '.join(BACKENDS)})"
        )

    # GNOME is the default (preserves pre-provider behavior); ewmh is the fallback.
    if desktop in ("gnome", "unknown"):
        workspace: WorkspaceProvider = GnomeWorkspaceProvider(dev_mode=dev_mode)
        extensions: ExtensionProvider = GnomeExtensionProvider(dev_mode=dev_mode)
    elif desktop == "kde":
        workspace = KdeWorkspaceProvider(dev_mode=dev_mode)
        extensions = KdeExtensionProvider(dev_mode=dev_mode)
    elif desktop == "hyprland":
        workspace = HyprlandWorkspaceProvider(dev_mode=dev_mode)
        extensions = NullExtensionProvider(desktop=desktop, dev_mode=dev_mode)
    elif desktop == "sway":
        workspace = SwayWorkspaceProvider(dev_mode=dev_mode)
        extensions = NullExtensionProvider(desktop=desktop, dev_mode=dev_mode)
    elif desktop == "wlroots":
        workspace = WlrootsWorkspaceProvider(dev_mode=dev_mode)
        extensions = NullExtensionProvider(desktop=desktop, dev_mode=dev_mode)
    else:
        workspace = EwmhWorkspaceProvider(dev_mode=dev_mode)
        extensions = NullExtensionProvider(desktop=desktop, dev_mode=dev_mode)

    tools = profile.tool_availability or {}
    if tools.get("wofi") or tools.get("rofi"):
        display: DisplayProvider = RofiDisplayProvider(dev_mode=dev_mode)
    else:
        display = TuiDisplayProvider(dev_mode=dev_mode)

    return workspace, display, extensions


__all__: list[str] = [
    "BACKENDS",
    "DesktopProfile",
    "TOOL_REQUIREMENTS",
    "detect_desktop",
    "get_providers",
]
