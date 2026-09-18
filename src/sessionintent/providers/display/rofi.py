"""
SessionIntent UI Selector
Provides mode selection using wofi or rofi.
"""

from __future__ import annotations

import subprocess
from typing import Any

from ...hardware import is_on_ac


def select_mode(config: dict[str, Any]) -> str | None:
    """
    Display mode selection menu and return selected mode.

    Args:
        config: Full configuration dictionary

    Returns:
        Selected mode key, or None if no selection
    """
    available_modes = get_available_modes(config)
    return present_modes(available_modes)


def present_modes(modes: dict[str, Any]) -> str | None:
    """
    Present already-filtered modes in wofi/rofi and return the selection.

    Args:
        modes: Filtered mode configurations

    Returns:
        Selected mode key, or None if no selection
    """
    if not modes:
        return None

    menu_entries = format_menu_entries(modes)
    input_str = "\n".join(menu_entries)

    selector = find_selector()
    if not selector:
        print("Error: wofi or rofi not found.")
        return None

    cmd = build_selector_command(selector, menu_entries)

    try:
        result = subprocess.run(cmd, input=input_str, text=True, capture_output=True)

        if result.returncode == 0:
            choice = result.stdout.strip()
            if choice:
                return parse_selection(choice, modes)

        return None
    except Exception as e:
        print(f"UI Error: {e}")
        return None


def get_available_modes(config: dict[str, Any]) -> dict[str, Any]:
    """Get modes based on current hardware state."""
    all_modes = config.get("modes", {})

    if not is_on_ac():
        battery_profile = config.get("hardware_profiles", {}).get("battery", {})
        disabled = battery_profile.get("disable_modes", [])
        return {k: v for k, v in all_modes.items() if k not in disabled}

    return all_modes


def find_selector() -> str | None:
    """Find available selector tool (wofi or rofi)."""
    for cmd in ["wofi", "rofi"]:
        try:
            result = subprocess.run(["which", cmd], capture_output=True, check=True)
            if result.returncode == 0:
                return cmd
        except subprocess.CalledProcessError:
            continue

    return None


def build_selector_command(selector: str, menu_entries: list[str]) -> list[str]:
    """Build the wofi/rofi command for mode selection."""
    cmd = [selector, "-dmenu", "-p", "Select Session Mode", "-i"]

    if selector == "wofi":
        cmd += ["--lines", str(len(menu_entries) + 1)]

    return cmd


def format_menu_entries(modes: dict[str, Any]) -> list[str]:
    """Format mode entries for display in selector."""
    entries = []
    mode_keys = list(modes.keys())

    for i, key in enumerate(mode_keys):
        label = modes[key].get("label", key)
        entries.append(f"{i + 1}: {label}")

    return entries


def parse_selection(choice: str, modes: dict[str, Any]) -> str | None:
    """Parse user selection and return mode key."""
    mode_keys = list(modes.keys())

    try:
        # Try numeric selection first (wofi output)
        idx = int(choice.split(":")[0]) - 1
        if 0 <= idx < len(mode_keys):
            return mode_keys[idx]
    except (ValueError, IndexError):
        pass

    # Try to match by label
    for key in mode_keys:
        label = modes[key].get("label", key)
        if choice.endswith(label):
            return key

    return None


class RofiDisplayProvider:
    """Mode selection via wofi/rofi."""

    def __init__(self, dev_mode: bool = False) -> None:
        self._dev_mode = dev_mode

    def select_mode(self, modes: dict[str, Any]) -> str | None:
        return present_modes(modes)

    def format_menu(self, modes: dict[str, Any]) -> list[str]:
        return format_menu_entries(modes)

    def find_selector(self) -> str | None:
        return find_selector()


__all__ = [
    "select_mode",
    "present_modes",
    "get_available_modes",
    "find_selector",
    "build_selector_command",
    "format_menu_entries",
    "parse_selection",
    "RofiDisplayProvider",
]
