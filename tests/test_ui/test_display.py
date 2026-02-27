"""Tests for UI display utilities."""

import pytest

from src.ui.display import (
    format_mode_menu,
    format_menu_entries,
    format_mode_info,
    format_app_info,
    format_error,
    format_success,
)


class TestFormatModeMenu:
    """Test format_mode_menu function."""

    @pytest.mark.parametrize(
        "modes,expected",
        [
            ({"work": {"label": "Work"}}, "1: Work"),
            ({"work": {"label": "Work"}, "gaming": {"label": "Gaming"}}, "1: Work"),
            ({}, ""),
            ({"browsing": {}}, "1: browsing"),
        ],
    )
    def test_format_mode_menu(self, modes, expected):
        """Test formatting modes."""
        result = format_mode_menu(modes)
        assert expected in result


class TestFormatMenuEntries:
    """Test format_menu_entries function."""

    @pytest.mark.parametrize(
        "modes,expected",
        [
            ({"work": {"label": "Work"}}, ["1: Work"]),
            (
                {"a": {"label": "Alpha"}, "b": {"label": "Beta"}},
                ["1: Alpha", "2: Beta"],
            ),
            ({}, []),
            ({"work": {}}, ["1: work"]),
        ],
    )
    def test_format_menu_entries(self, modes, expected):
        """Test formatting menu entries."""
        assert format_menu_entries(modes) == expected


class TestFormatModeInfo:
    """Test format_mode_info function."""

    @pytest.mark.parametrize(
        "mode_key,config,expected",
        [
            ("work", {"label": "Work"}, "Mode: work"),
            ("work", {"label": "Work", "description": "Test"}, "Description: Test"),
            (
                "work",
                {"label": "Work", "workspaces": {"1": ["firefox"]}},
                "Workspaces:",
            ),
        ],
    )
    def test_format_mode_info(self, mode_key, config, expected):
        """Test formatting mode info."""
        result = format_mode_info(mode_key, config)
        assert expected in result


class TestFormatAppInfo:
    """Test format_app_info function."""

    @pytest.mark.parametrize(
        "app_key,app_def,expected",
        [
            ("firefox", {"cmd": ["firefox"]}, "App: firefox"),
            ("firefox", {"cmd": ["firefox"], "check": "fx"}, "Check pattern: fx"),
            ("app", {"cmd": ["app"], "flags": {"v": "-v"}}, "Flags:"),
            ("app", {"cmd": ["app"], "internal_reuse": False}, "Internal reuse: False"),
        ],
    )
    def test_format_app_info(self, app_key, app_def, expected):
        """Test formatting app info."""
        result = format_app_info(app_key, app_def)
        assert expected in result


class TestFormatError:
    """Test format_error function."""

    @pytest.mark.parametrize(
        "msg,expected",
        [
            ("Something wrong", "[ERROR] Something wrong"),
            ("", "[ERROR] "),
        ],
    )
    def test_format_error(self, msg, expected):
        """Test error formatting."""
        assert format_error(msg) == expected


class TestFormatSuccess:
    """Test format_success function."""

    @pytest.mark.parametrize(
        "msg,expected",
        [
            ("Done", "[SUCCESS] Done"),
            ("", "[SUCCESS] "),
        ],
    )
    def test_format_success(self, msg, expected):
        """Test success formatting."""
        assert format_success(msg) == expected
