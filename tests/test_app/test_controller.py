"""Tests for app controller."""

import pytest
from unittest.mock import patch, MagicMock

from src.app.controller import (
    is_running,
    launch_app,
    _build_command,
    _print,
    _print_or_launch,
    resolve_template,
)


class TestIsRunning:
    """Test is_running function."""

    def test_is_running_dev_mode(self):
        """Test is_running in dev mode always returns False."""
        assert is_running("firefox", dev_mode=True) is False

    @patch("subprocess.run")
    def test_is_running_found(self, mock_run):
        """Test is_running when process is found."""
        mock_run.return_value = MagicMock()
        assert is_running("firefox", dev_mode=False) is True

    @patch("subprocess.run")
    def test_is_running_not_found(self, mock_run):
        """Test is_running when process is not found."""
        from subprocess import CalledProcessError

        mock_run.side_effect = CalledProcessError(1, "pgrep")
        assert is_running("nonexistent", dev_mode=False) is False


class TestBuildCommand:
    """Test _build_command function."""

    def test_build_simple_command(self):
        """Test building simple command."""
        app_def = {"cmd": ["firefox"]}
        cmd = _build_command(app_def, {})
        assert cmd == ["firefox"]

    def test_build_command_with_flags(self):
        """Test building command with flags."""
        app_def = {"cmd": ["app"], "flags": {"verbose": "-v"}}
        cmd = _build_command(app_def, {"verbose": True})
        assert "-v" in cmd

    def test_build_command_with_append_param(self):
        """Test building command with append_param."""
        app_def = {"cmd": ["app"], "append_param": "urls"}
        cmd = _build_command(app_def, {"urls": ["http://a.com"]})
        assert "http://a.com" in cmd

    def test_build_command_with_append_param_single(self):
        """Test building command with single append_param."""
        app_def = {"cmd": ["app"], "append_param": "url"}
        cmd = _build_command(app_def, {"url": "http://test.com"})
        assert "http://test.com" in cmd


class TestLaunchApp:
    """Test launch_app function."""

    def test_launch_app_dev_mode(self, capsys):
        """Test launching app in dev mode."""
        apps = {"firefox": {"cmd": ["firefox"]}}
        launch_app("firefox", {}, apps, dev_mode=True)
        captured = capsys.readouterr()
        assert "firefox" in captured.out

    def test_launch_app_not_in_registry(self, capsys):
        """Test launching app not in registry."""
        launch_app("unknown", {}, {}, dev_mode=True)
        captured = capsys.readouterr()
        assert "unknown" in captured.out

    @patch("subprocess.Popen")
    @patch("src.app.controller.is_running", return_value=False)
    def test_launch_app_real_mode(self, mock_is_running, mock_popen):
        """Test launching app in real mode."""
        apps = {"firefox": {"cmd": ["firefox"]}}
        launch_app("firefox", {}, apps, dev_mode=False)
        mock_popen.assert_called_once()

    @patch("subprocess.Popen")
    @patch("src.app.controller.is_running", return_value=True)
    def test_launch_app_skip_when_running_no_reuse(self, mock_is_running, mock_popen):
        """Test launching app skips when already running and internal_reuse=False."""
        apps = {
            "firefox": {"cmd": ["firefox"], "check": "firefox", "internal_reuse": False}
        }
        launch_app("firefox", {}, apps, dev_mode=False)
        mock_popen.assert_not_called()


class TestPrintFunctions:
    """Test _print and _print_or_launch functions."""

    def test_print_dev_mode(self, capsys):
        """Test _print in dev mode."""
        _print(True, "test message")
        captured = capsys.readouterr()
        assert "test message" in captured.out

    def test_print_or_launch_dev_mode(self, capsys):
        """Test _print_or_launch in dev mode."""
        _print_or_launch(["cmd"], dev_mode=True)
        captured = capsys.readouterr()
        assert "cmd" in captured.out

    @patch("subprocess.Popen")
    def test_print_or_launch_real_mode(self, mock_popen):
        """Test _print_or_launch in real mode."""
        _print_or_launch(["cmd"], dev_mode=False)
        mock_popen.assert_called_once()


class TestResolveTemplateController:
    """Test resolve_template in controller module."""

    def test_resolve_template_basic(self):
        """Test basic template resolution in controller."""
        assert resolve_template("hello {name}", {"name": "World"}) == "hello World"

    def test_resolve_template_with_default(self):
        """Test template with default value."""
        assert resolve_template("hello {name|stranger}", {}) == "hello stranger"

    def test_resolve_template_none_value(self):
        """Test template with None value uses default."""
        assert resolve_template("hi {n|x}", {"n": None}) == "hi x"

    def test_resolve_template_empty_string(self):
        """Test resolving empty string."""
        assert resolve_template("", {}) == ""


class TestBuildCommandAdvanced:
    """Test _build_command with more scenarios."""

    def test_build_command_with_template_in_cmd(self):
        """Test building command with template in cmd parts."""
        app_def = {"cmd": ["app", "{arg}"]}
        cmd = _build_command(app_def, {"arg": "value"})
        assert "value" in cmd

    def test_build_command_with_empty_resolved(self):
        """Test building command with empty resolved template."""
        app_def = {"cmd": ["app", "{arg}"]}
        cmd = _build_command(app_def, {})
        assert "app" in cmd

    def test_build_command_with_flags_params(self):
        """Test building command with flag params."""
        app_def = {"cmd": ["app"], "flags": {"verbose": "-v", "quiet": "-q"}}
        cmd = _build_command(app_def, {"verbose": True, "quiet": False})
        assert "-v" in cmd
        assert "-q" not in cmd

    def test_build_command_append_list(self):
        """Test building command with append_param as list."""
        app_def = {"cmd": ["app"], "append_param": "urls"}
        cmd = _build_command(app_def, {"urls": ["url1", "url2"]})
        assert "url1" in cmd
        assert "url2" in cmd

    def test_build_command_append_single(self):
        """Test building command with append_param as single value."""
        app_def = {"cmd": ["app"], "append_param": "url"}
        cmd = _build_command(app_def, {"url": "single_url"})
        assert "single_url" in cmd


class TestLaunchAppAdvanced:
    """Test launch_app with more scenarios."""

    @patch("subprocess.Popen")
    @patch("src.app.controller.is_running", return_value=True)
    def test_launch_app_running_with_reuse(self, mock_is_running, mock_popen, capsys):
        """Test launching app that's already running with reuse enabled."""
        apps = {
            "firefox": {"cmd": ["firefox"], "check": "firefox", "internal_reuse": True}
        }
        launch_app("firefox", {}, apps, dev_mode=True)
        mock_popen.assert_not_called()
        captured = capsys.readouterr()
        assert "reusing" in captured.out

    @patch("src.app.controller.is_running")
    def test_launch_app_check_is_false(self, mock_is_running, capsys):
        """Test launching app with check=False skips running check."""
        apps = {"app": {"cmd": ["app"], "check": False}}
        launch_app("app", {}, apps, dev_mode=True)
        mock_is_running.assert_not_called()
        captured = capsys.readouterr()
        assert "app" in captured.out
