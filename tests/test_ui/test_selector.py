"""Tests for UI selector."""

import pytest
from unittest.mock import patch, MagicMock

from src.ui.selector import (
    select_mode,
    find_selector,
    build_selector_command,
    parse_selection,
)


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
