"""
SessionIntent UI Package
Provides user interface components (selectors, display).
"""

from .selector import select_mode, get_available_modes, find_selector
from .display import (
    format_mode_menu,
    format_menu_entries,
    format_mode_info,
    format_app_info,
    format_error,
    format_success,
)
from .theme import (
    load_theme,
    list_themes,
    get_current_theme,
    set_theme,
    apply_theme_colors,
    DEFAULT_THEME,
    BUILT_IN_THEMES,
)

__all__ = [
    # Selector
    "select_mode",
    "get_available_modes",
    "find_selector",
    # Display
    "format_mode_menu",
    "format_menu_entries",
    "format_mode_info",
    "format_app_info",
    "format_error",
    "format_success",
    # Theme
    "load_theme",
    "list_themes",
    "get_current_theme",
    "set_theme",
    "apply_theme_colors",
    "DEFAULT_THEME",
    "BUILT_IN_THEMES",
]
