"""
SessionIntent Theme Support
Provides theme management for the TUI/UI.
"""

from __future__ import annotations

import os
from typing import Any

from ..constants import CONFIG_DIR
from ..session.log import info, warning

THEME_DIR = CONFIG_DIR / "themes"


class ThemeColors:
    """Theme color palette."""

    def __init__(
        self,
        primary: str = "blue",
        secondary: str = "white",
        background: str = "black",
        foreground: str = "white",
        success: str = "green",
        error: str = "red",
        warning: str = "yellow",
        highlight: str = "cyan",
    ) -> None:
        self.primary = primary
        self.secondary = secondary
        self.background = background
        self.foreground = foreground
        self.success = success
        self.error = error
        self.warning = warning
        self.highlight = highlight


class Theme:
    """UI Theme."""

    def __init__(
        self,
        name: str,
        colors: ThemeColors,
        styles: dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.colors = colors
        self.styles = styles or {}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Theme:
        """Create theme from dict."""
        colors = ThemeColors(**data.get("colors", {}))
        return cls(
            name=data.get("name", "default"),
            colors=colors,
            styles=data.get("styles", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert theme to dict."""
        return {
            "name": self.name,
            "colors": {
                "primary": self.colors.primary,
                "secondary": self.colors.secondary,
                "background": self.colors.background,
                "foreground": self.colors.foreground,
                "success": self.colors.success,
                "error": self.colors.error,
                "warning": self.colors.warning,
                "highlight": self.colors.highlight,
            },
            "styles": self.styles,
        }


DEFAULT_THEME = Theme(
    name="default",
    colors=ThemeColors(),
)


BUILT_IN_THEMES: dict[str, Theme] = {
    "default": DEFAULT_THEME,
    "dark": Theme(
        name="dark",
        colors=ThemeColors(
            primary="darkblue",
            secondary="darkgray",
            background="black",
            foreground="lightgray",
            success="darkgreen",
            error="darkred",
            warning="darkyellow",
            highlight="darkcyan",
        ),
    ),
    "light": Theme(
        name="light",
        colors=ThemeColors(
            primary="blue",
            secondary="white",
            background="white",
            foreground="black",
            success="green",
            error="red",
            warning="yellow",
            highlight="cyan",
        ),
    ),
    "gruvbox": Theme(
        name="gruvbox",
        colors=ThemeColors(
            primary="lightred",
            secondary="lightyellow",
            background="#282828",
            foreground="#ebdbb2",
            success="#98971a",
            error="#cc241d",
            warning="#d79921",
            highlight="#83a598",
        ),
    ),
    "nord": Theme(
        name="nord",
        colors=ThemeColors(
            primary="lightblue",
            secondary="white",
            background="#2e3440",
            foreground="#d8dee9",
            success="#a3be8c",
            error="#bf616a",
            warning="#ebcb8b",
            highlight="#88c0d0",
        ),
    ),
}


def load_theme(theme_name: str) -> Theme:
    """
    Load a theme by name.

    Args:
        theme_name: Name of the theme to load

    Returns:
        Theme instance
    """
    if theme_name in BUILT_IN_THEMES:
        return BUILT_IN_THEMES[theme_name]

    theme_file = THEME_DIR / f"{theme_name}.yaml"

    if not theme_file.exists():
        warning(f"Theme '{theme_name}' not found, using default")
        return DEFAULT_THEME

    import yaml

    try:
        with open(theme_file, "r") as f:
            data = yaml.safe_load(f)
            return Theme.from_dict(data)
    except (yaml.YAMLError, IOError):
        warning(f"Failed to load theme '{theme_name}', using default")
        return DEFAULT_THEME


def list_themes() -> list[str]:
    """List available themes."""
    themes = list(BUILT_IN_THEMES.keys())

    if THEME_DIR.exists():
        for file_path in THEME_DIR.glob("*.yaml"):
            name = file_path.stem
            if name not in BUILT_IN_THEMES:
                themes.append(name)

    return sorted(themes)


def get_current_theme() -> Theme:
    """Get the current theme from config."""
    theme_name = os.environ.get("SESSIONINTENT_THEME", "default")
    return load_theme(theme_name)


def set_theme(theme_name: str) -> bool:
    """Set the current theme."""
    theme = load_theme(theme_name)
    os.environ["SESSIONINTENT_THEME"] = theme.name
    info(f"Theme set to: {theme.name}")
    return True


def apply_theme_colors(
    theme: Theme,
) -> dict[str, str]:
    """Apply theme colors as environment variables."""
    colors = theme.colors
    return {
        "SESSIONINTENT_COLOR_PRIMARY": colors.primary,
        "SESSIONINTENT_COLOR_SECONDARY": colors.secondary,
        "SESSIONINTENT_COLOR_BG": colors.background,
        "SESSIONINTENT_COLOR_FG": colors.foreground,
        "SESSIONINTENT_COLOR_SUCCESS": colors.success,
        "SESSIONINTENT_COLOR_ERROR": colors.error,
        "SESSIONINTENT_COLOR_WARNING": colors.warning,
        "SESSIONINTENT_COLOR_HIGHLIGHT": colors.highlight,
    }


__all__ = [
    "Theme",
    "ThemeColors",
    "DEFAULT_THEME",
    "BUILT_IN_THEMES",
    "load_theme",
    "list_themes",
    "get_current_theme",
    "set_theme",
    "apply_theme_colors",
]