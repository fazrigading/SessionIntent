"""
SessionIntent TUI Display Provider
Terminal fallback: numbered menu on stdout, choice on stdin.
"""

from __future__ import annotations

from typing import Any

from .rofi import format_menu_entries, parse_selection


class TuiDisplayProvider:
    """Terminal-based mode selection (universal fallback)."""

    def __init__(self, dev_mode: bool = False) -> None:
        self._dev_mode = dev_mode

    def format_menu(self, modes: dict[str, Any]) -> list[str]:
        return format_menu_entries(modes)

    def find_selector(self) -> str | None:
        return None

    def select_mode(self, modes: dict[str, Any]) -> str | None:
        """
        Print a numbered menu and read the choice from stdin.

        Returns:
            Selected mode key, or None on empty/invalid input or EOF.
        """
        if not modes:
            return None
        print("Select mode:")
        for entry in format_menu_entries(modes):
            print(f"  {entry}")
        try:
            choice = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            return None
        if not choice:
            return None
        try:
            idx = int(choice.split(":")[0]) - 1
            keys = list(modes.keys())
            if 0 <= idx < len(keys):
                return keys[idx]
        except ValueError:
            pass
        return parse_selection(choice, modes)


__all__ = ["TuiDisplayProvider"]
