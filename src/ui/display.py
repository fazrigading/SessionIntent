"""
SessionIntent UI Display
Provides utilities for formatting and displaying UI elements.
"""

from __future__ import annotations

from typing import Any


def format_mode_menu(modes: dict[str, Any]) -> str:
    """
    Format modes into a display-ready string for menu selectors.

    Args:
        modes: Dictionary of mode configurations

    Returns:
        String with one mode per line in format "N: Label"
    """
    entries = format_menu_entries(modes)
    return "\n".join(entries)


def format_menu_entries(modes: dict[str, Any]) -> list[str]:
    """
    Format modes into a list of menu entries.

    Args:
        modes: Dictionary of mode configurations

    Returns:
        List of formatted strings like ["1: Browsing / Chilling"]
    """
    entries = []
    mode_keys = list(modes.keys())

    for i, key in enumerate(mode_keys):
        label = modes[key].get("label", key)
        entries.append(f"{i + 1}: {label}")

    return entries


def format_mode_info(mode_key: str, mode_config: dict[str, Any]) -> str:
    """Format a single mode's info for display."""
    label = mode_config.get("label", mode_key)
    info = [f"Mode: {mode_key}"]
    info.append(f"Label: {label}")

    # Add description if present
    if "description" in mode_config:
        info.append(f"Description: {mode_config['description']}")

    # Show workspaces
    workspaces = mode_config.get("workspaces", {})
    if workspaces:
        info.append("Workspaces:")
        for ws_num, ws_value in sorted(workspaces.items(), key=lambda x: int(x[0])):
            if isinstance(ws_value, dict):
                apps = ws_value.get("apps", [])
                monitor = ws_value.get("monitor")
                app_str = ", ".join(str(a) for a in apps)
                if monitor:
                    info.append(f"  {ws_num} ({monitor}): {app_str}")
                else:
                    info.append(f"  {ws_num}: {app_str}")
            else:
                app_str = ", ".join(str(a) for a in ws_value)
                info.append(f"  {ws_num}: {app_str}")

    return "\n".join(info)


def format_app_info(app_key: str, app_def: dict[str, Any]) -> str:
    """Format an app's definition for display."""
    lines = [f"App: {app_key}"]

    cmd = app_def.get("cmd", [app_key])
    lines.append(f"Command: {' '.join(cmd)}")

    if "check" in app_def:
        lines.append(f"Check pattern: {app_def['check']}")

    if "flags" in app_def:
        lines.append(f"Flags: {app_def['flags']}")

    if "append_param" in app_def:
        lines.append(f"Append param: {app_def['append_param']}")

    if "internal_reuse" in app_def:
        lines.append(f"Internal reuse: {app_def['internal_reuse']}")

    return "\n".join(lines)


def format_error(message: str) -> str:
    """Format an error message for consistent display."""
    return f"[ERROR] {message}"


def format_success(message: str) -> str:
    """Format a success message for consistent display."""
    return f"[SUCCESS] {message}"
