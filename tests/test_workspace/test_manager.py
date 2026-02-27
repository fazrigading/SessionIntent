"""Tests for workspace manager."""

import pytest
from unittest.mock import patch, MagicMock

from src.workspace.manager import (
    switch_workspace,
    get_current_workspace,
    get_all_workspace_names,
    get_workspace_count,
)


class TestSwitchWorkspace:
    """Test switch_workspace function."""

    def test_switch_workspace_dev_mode(self, capsys):
        """Test switching workspace in dev mode."""
        switch_workspace(1, dev_mode=True)
        captured = capsys.readouterr()
        assert "Switching to workspace 1" in captured.out

    def test_switch_workspace_dev_mode_multiple(self, capsys):
        """Test switching to different workspaces in dev mode."""
        switch_workspace(3, dev_mode=True)
        captured = capsys.readouterr()
        assert "Switching to workspace 3" in captured.out

    @patch("subprocess.run")
    def test_switch_workspace_real_mode(self, mock_run):
        """Test switching workspace in real mode."""
        mock_run.return_value = MagicMock()
        switch_workspace(1, dev_mode=False)
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_switch_workspace_zero_indexed_conversion(self, mock_run):
        """Test that workspace number is converted from 1-indexed to 0-indexed."""
        mock_run.return_value = MagicMock()
        switch_workspace(1, dev_mode=False)
        call_args = mock_run.call_args[0][0]
        # The command is: gdbus call ... --method org.gnome.Shell.Eval "Main.wm.actionMoveWorkspace..."
        # Find the full method argument (last element)
        method_arg = call_args[-1]
        assert method_arg is not None
        assert "get_workspace_by_index(0)" in method_arg

    @patch("subprocess.run")
    def test_switch_workspace_error_handling(self, mock_run):
        """Test error handling when gdbus fails."""
        mock_run.side_effect = Exception("DBus error")
        switch_workspace(1, dev_mode=False)


class TestGetCurrentWorkspace:
    """Test get_current_workspace function."""

    def test_get_current_workspace_dev_mode(self):
        """Test getting current workspace in dev mode."""
        result = get_current_workspace(dev_mode=True)
        assert result == 1

    @patch("subprocess.run")
    def test_get_current_workspace_real_mode(self, mock_run):
        """Test getting current workspace in real mode."""
        mock_run.return_value = MagicMock(stdout="(uint32 2,)")
        result = get_current_workspace(dev_mode=False)
        assert result == 3  # 0-indexed + 1

    @patch("subprocess.run")
    def test_get_current_workspace_no_gnome(self, mock_run):
        """Test getting current workspace when GNOME not available."""
        mock_run.side_effect = Exception("No GNOME")
        result = get_current_workspace(dev_mode=False)
        assert result is None


class TestGetAllWorkspaceNames:
    """Test get_all_workspace_names function."""

    def test_get_all_workspace_names_dev_mode(self):
        """Test getting workspace names in dev mode."""
        result = get_all_workspace_names(dev_mode=True)
        assert result == ["Workspace 1"]

    @patch("subprocess.run")
    def test_get_all_workspace_names_real_mode(self, mock_run):
        """Test getting workspace names in real mode."""
        mock_run.return_value = MagicMock(stdout='["Work", "Web", "Chat"]')
        result = get_all_workspace_names(dev_mode=False)
        assert result == ["Work", "Web", "Chat"]

    @patch("subprocess.run")
    def test_get_all_workspace_names_empty(self, mock_run):
        """Test getting workspace names when none exist."""
        mock_run.return_value = MagicMock(stdout="[]")
        result = get_all_workspace_names(dev_mode=False)
        assert result == []

    @patch("subprocess.run")
    def test_get_all_workspace_names_error(self, mock_run):
        """Test error handling when getting workspace names fails."""
        mock_run.side_effect = Exception("DBus error")
        result = get_all_workspace_names(dev_mode=False)
        assert result == []


class TestGetWorkspaceCount:
    """Test get_workspace_count function."""

    def test_get_workspace_count_dev_mode(self):
        """Test getting workspace count in dev mode."""
        result = get_workspace_count(dev_mode=True)
        assert result == 1

    @patch("subprocess.run")
    def test_get_workspace_count_real_mode(self, mock_run):
        """Test getting workspace count in real mode."""
        mock_run.return_value = MagicMock(stdout="(uint32 3,)")
        result = get_workspace_count(dev_mode=False)
        assert result == 3

    @patch("subprocess.run")
    def test_get_workspace_count_error(self, mock_run):
        """Test error handling when getting workspace count fails."""
        mock_run.side_effect = Exception("DBus error")
        result = get_workspace_count(dev_mode=False)
        assert result == 1  # Default fallback
