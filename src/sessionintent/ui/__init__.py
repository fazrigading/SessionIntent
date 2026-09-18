"""
SessionIntent UI Package
Compatibility re-exports; new code should use sessionintent.providers.
"""

from ..providers.display.rofi import (
    RofiDisplayProvider,
    build_selector_command,
    find_selector,
    format_menu_entries,
    get_available_modes,
    parse_selection,
    present_modes,
    select_mode,
)
from .display import (
    format_app_info,
    format_error,
    format_menu_entries as format_menu_entries_display,
    format_mode_info,
    format_mode_menu,
    format_success,
)
from ..providers.display.tui import TuiDisplayProvider

__all__ = [
    # Selector (provider-backed)
    "RofiDisplayProvider",
    "TuiDisplayProvider",
    "select_mode",
    "present_modes",
    "get_available_modes",
    "find_selector",
    "build_selector_command",
    "format_menu_entries",
    "parse_selection",
    # Display formatting
    "format_mode_menu",
    "format_menu_entries_display",
    "format_mode_info",
    "format_app_info",
    "format_error",
    "format_success",
]
