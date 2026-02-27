"""Tests for UI selector."""

import pytest
from unittest.mock import patch, MagicMock

from src.ui.selector import (
    select_mode,
    get_available_modes,
    find_selector,
    build_selector_command,
    format_menu_entries,
    parse_selection,
)


class TestGetAvailableModes:
    """Test get_available_modes function."""

    @patch("src.ui.selector.is_on_ac", return_value=True)
    def test_get_available_modes_ac_power(self, mock_is_on_ac):
        """Test get_available_modes on AC power returns all modes."""
        config = {"modes": {"work": {}, "gaming": {}}}
        modes = get_available_modes(config)
        assert "work" in modes
        assert "gaming" in modes

    @patch("src.ui.selector.is_on_ac", return_value=False)
    def test_get_available_modes_battery_disabled(self, mock_is_on_ac):
        """Test get_available_modes on battery with disabled modes."""
        config = {
            "modes": {"work": {}, "gaming": {}},
            "hardware_profiles": {"battery": {"disable_modes": ["gaming"]}},
        }
        modes = get_available_modes(config)
        assert "work" in modes
        assert "gaming" not in modes


class TestFindSelector:
    """Test find_selector function."""

    @patch("subprocess.run")
    def test_find_selector_wofi(self, mock_run):
        """Test finding wofi selector."""
        mock_run.return_value = MagicMock(returncode=0)
        result = find_selector()
        assert result == "wofi"

    @patch("subprocess.run")
    def test_find_selector_rofi(self, mock_run):
        """Test finding rofi selector when wofi not found."""
        from subprocess import CalledProcessError

        def side_effect(*args, **kwargs):
            if args[0][1] == "wofi":
                raise CalledProcessError(1, "which")
            return MagicMock(returncode=0)

        mock_run.side_effect = side_effect
        result = find_selector()
        assert result == "rofi"

    @patch("subprocess.run")
    def test_find_selector_none(self, mock_run):
        """Test find_selector when no selector found."""
        from subprocess import CalledProcessError

        mock_run.side_effect = CalledProcessError(1, "which")
        result = find_selector()
        assert result is None


class TestBuildSelectorCommand:
    """Test build_selector_command function."""

    def test_build_wofi_command(self):
        """Test building wofi command."""
        cmd = build_selector_command("wofi", ["a", "b", "c"])
        assert "wofi" in cmd
        assert "-dmenu" in cmd

    def test_build_rofi_command(self):
        """Test building rofi command."""
        cmd = build_selector_command("rofi", ["a", "b"])
        assert "rofi" in cmd
        assert "-dmenu" in cmd


class TestFormatMenuEntries:
    """Test format_menu_entries function."""

    def test_format_single_entry(self):
        """Test formatting single menu entry."""
        entries = format_menu_entries({"work": {"label": "Work"}})
        assert "1: Work" in entries

    def test_format_multiple_entries(self):
        """Test formatting multiple menu entries."""
        entries = format_menu_entries({"a": {"label": "A"}, "b": {"label": "B"}})
        assert len(entries) == 2

    def test_format_no_label(self):
        """Test formatting entry without label uses key."""
        entries = format_menu_entries({"custom": {}})
        assert "1: custom" in entries


class TestParseSelection:
    """Test parse_selection function."""

    def test_parse_numeric_selection(self):
        """Test parsing numeric selection."""
        modes = {"work": {}, "gaming": {}}
        result = parse_selection("1: Work", modes)
        assert result == "work"

    def test_parse_label_selection(self):
        """Test parsing label selection."""
        modes = {"work": {"label": "Work Mode"}}
        result = parse_selection("Work Mode", modes)
        assert result == "work"

    def test_parse_invalid_selection(self):
        """Test parsing invalid selection returns None."""
        modes = {"work": {}}
        result = parse_selection("999", modes)
        assert result is None
