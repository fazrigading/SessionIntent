"""Tests for workspace manager."""

from unittest.mock import patch, MagicMock
import subprocess

from src.workspace.manager import (
    switch_workspace,
    get_current_workspace,
    get_workspace_count,
    ensure_extension,
    wait_for_workspace,
    _socket_call,
    _is_extension_available,
    _gdbus_workspace_call,
)


class TestSocketCall:
    """Test _socket_call helper."""

    def test_socket_call_dev_mode_current(self):
        """Test socket call CURRENT in dev mode."""
        ok, resp = _socket_call("CURRENT\n", dev_mode=True)
        assert ok is True
        assert resp == "0"

    def test_socket_call_dev_mode_switch(self):
        """Test socket call SWITCH in dev mode."""
        ok, resp = _socket_call("SWITCH 1\n", dev_mode=True)
        assert ok is True
        assert resp == "OK"

    def test_socket_call_dev_mode_count(self):
        """Test socket call COUNT in dev mode."""
        ok, resp = _socket_call("COUNT\n", dev_mode=True)
        assert ok is True
        assert resp == "4"

    

    @patch("src.workspace.manager._get_socket_path")
    def test_socket_call_no_runtime_dir(self, mock_get_path):
        """Test socket call when XDG_RUNTIME_DIR not set."""
        mock_get_path.return_value = None
        ok, resp = _socket_call("CURRENT\n")
        assert ok is False
        assert "XDG_RUNTIME_DIR" in resp

    @patch("src.workspace.manager._get_socket_path")
    def test_socket_call_socket_not_found(self, mock_get_path):
        """Test socket call when socket doesn't exist."""
        mock_get_path.return_value = "/tmp/nonexistent.sock"
        ok, resp = _socket_call("CURRENT\n")
        assert ok is False
        assert "not found" in resp.lower()


class TestIsExtensionAvailable:
    """Test _is_extension_available helper."""

    def test_dev_mode(self):
        """Test extension availability check in dev mode."""
        assert _is_extension_available(dev_mode=True) is True

    @patch("src.workspace.manager._socket_call")
    def test_socket_available(self, mock_socket_call):
        """Test when socket is available."""
        mock_socket_call.return_value = (True, "0")
        assert _is_extension_available(dev_mode=False) is True

    @patch("src.workspace.manager._socket_call")
    def test_socket_not_available(self, mock_socket_call):
        """Test when socket is not available."""
        mock_socket_call.return_value = (False, "Socket not found")
        assert _is_extension_available(dev_mode=False) is False


class TestGdbusWorkspaceCall:
    """Test _gdbus_workspace_call helper."""

    def test_dev_mode(self):
        """Test gdbus call in dev mode."""
        ok, resp = _gdbus_workspace_call("Main.wm.get_active_workspace_index()", dev_mode=True)
        assert ok is True
        assert "uint32" in resp

    @patch("subprocess.run")
    def test_real_mode_success(self, mock_run):
        """Test successful gdbus call."""
        mock_run.return_value = MagicMock(returncode=0, stdout="(uint32 2,)")
        ok, resp = _gdbus_workspace_call("Main.wm.get_active_workspace_index()", dev_mode=False)
        assert ok is True
        assert "uint32" in resp

    @patch("src.workspace.manager.subprocess.run")
    def test_real_mode_failure(self, mock_run):
        """Test failed gdbus call."""
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        ok, resp = _gdbus_workspace_call("Main.wm.get_active_workspace_index()", dev_mode=False)
        assert ok is False

    @patch("src.workspace.manager.subprocess.run")
    def test_timeout(self, mock_run):
        """Test gdbus call timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 5)
        ok, resp = _gdbus_workspace_call("Main.wm.get_active_workspace_index()", dev_mode=False)
        assert ok is False


class TestSwitchWorkspace:
    """Test switch_workspace function."""

    def test_switch_workspace_dev_mode(self, capsys):
        """Test switching workspace in dev mode."""
        result = switch_workspace(1, dev_mode=True)
        assert result is True
        captured = capsys.readouterr()
        assert "Switching to workspace 1" in captured.out

    def test_switch_workspace_dev_mode_with_monitor(self, capsys):
        """Test switching workspace with monitor in dev mode."""
        result = switch_workspace(2, dev_mode=True, monitor="HDMI-1")
        assert result is True
        captured = capsys.readouterr()
        assert "workspace 2" in captured.out
        assert "HDMI-1" in captured.out

    @patch("src.workspace.manager._is_extension_available")
    def test_switch_workspace_socket_success(self, mock_available):
        """Test switching via socket."""
        mock_available.return_value = True
        with patch("src.workspace.manager._socket_call") as mock_call:
            mock_call.return_value = (True, "OK")
            result = switch_workspace(3, dev_mode=False)
            assert result is True
            mock_call.assert_called_once()
            assert "SWITCH 2" in mock_call.call_args[0][0]

    @patch("src.workspace.manager._is_extension_available")
    def test_switch_workspace_socket_with_monitor(self, mock_available):
        """Test switching via socket with monitor."""
        mock_available.return_value = True
        with patch("src.workspace.manager._socket_call") as mock_call:
            mock_call.return_value = (True, "OK")
            result = switch_workspace(2, dev_mode=False, monitor="DP-1")
            assert result is True
            call_str = mock_call.call_args[0][0]
            assert "SWITCH 1" in call_str
            assert "DP-1" in call_str

    @patch("src.workspace.manager._is_extension_available")
    def test_switch_workspace_gdbus_fallback(self, mock_available):
        """Test gdbus fallback when socket unavailable."""
        mock_available.return_value = False
        with patch("src.workspace.manager._gdbus_workspace_call") as mock_gdbus:
            with patch("time.sleep"):
                mock_gdbus.return_value = (True, "")
                result = switch_workspace(2, dev_mode=False)
                assert result is True
                mock_gdbus.assert_called_once()

    @patch("src.workspace.manager._is_extension_available")
    def test_switch_workspace_all_methods_fail(self, mock_available):
        """Test failure when both socket and gdbus fail."""
        mock_available.return_value = False
        with patch("src.workspace.manager._gdbus_workspace_call") as mock_gdbus:
            mock_gdbus.return_value = (False, "error")
            result = switch_workspace(1, dev_mode=False)
            assert result is False


class TestWaitForWorkspace:
    """Test wait_for_workspace function."""

    def test_wait_dev_mode(self):
        """Test wait in dev mode returns immediately."""
        assert wait_for_workspace(1, dev_mode=True) is True

    @patch("src.workspace.manager.get_current_workspace")
    def test_wait_success(self, mock_current):
        """Test successful wait."""
        mock_current.side_effect = [1, 2, 3]
        result = wait_for_workspace(2, dev_mode=False, timeout=1.0)
        assert result is True
        assert mock_current.call_count == 2

    @patch("src.workspace.manager.get_current_workspace")
    def test_wait_timeout(self, mock_current):
        """Test wait times out."""
        mock_current.return_value = 1
        result = wait_for_workspace(2, dev_mode=False, timeout=0.1)
        assert result is False


class TestGetCurrentWorkspace:
    """Test get_current_workspace function."""

    def test_get_current_workspace_dev_mode(self):
        """Test getting current workspace in dev mode."""
        result = get_current_workspace(dev_mode=True)
        assert result == 1

    @patch("src.workspace.manager._is_extension_available")
    def test_get_current_workspace_socket(self, mock_available):
        """Test getting current workspace via socket."""
        mock_available.return_value = True
        with patch("src.workspace.manager._socket_call") as mock_call:
            mock_call.return_value = (True, "2")
            result = get_current_workspace(dev_mode=False)
            assert result == 3

    @patch("src.workspace.manager._is_extension_available")
    def test_get_current_workspace_gdbus_fallback(self, mock_available):
        """Test getting current workspace via gdbus."""
        mock_available.return_value = False
        with patch("src.workspace.manager._gdbus_workspace_call") as mock_gdbus:
            mock_gdbus.return_value = (True, "(uint32 2,)")
            result = get_current_workspace(dev_mode=False)
            assert result == 3

    @patch("src.workspace.manager._is_extension_available")
    def test_get_current_workspace_no_gnome(self, mock_available):
        """Test getting current workspace when GNOME not available."""
        mock_available.return_value = False
        with patch("src.workspace.manager._gdbus_workspace_call") as mock_gdbus:
            mock_gdbus.return_value = (False, "error")
            result = get_current_workspace(dev_mode=False)
            assert result is None


class TestGetWorkspaceCount:
    """Test get_workspace_count function."""

    def test_get_workspace_count_dev_mode(self):
        """Test getting workspace count in dev mode."""
        result = get_workspace_count(dev_mode=True)
        assert result == 1

    @patch("src.workspace.manager._is_extension_available")
    def test_get_workspace_count_socket(self, mock_available):
        """Test getting workspace count via socket."""
        mock_available.return_value = True
        with patch("src.workspace.manager._socket_call") as mock_call:
            mock_call.return_value = (True, "4")
            result = get_workspace_count(dev_mode=False)
            assert result == 4

    @patch("src.workspace.manager._is_extension_available")
    def test_get_workspace_count_gdbus_fallback(self, mock_available):
        """Test getting workspace count via gdbus."""
        mock_available.return_value = False
        with patch("src.workspace.manager._gdbus_workspace_call") as mock_gdbus:
            mock_gdbus.return_value = (True, "(uint32 3,)")
            result = get_workspace_count(dev_mode=False)
            assert result == 3

    @patch("src.workspace.manager._is_extension_available")
    def test_get_workspace_count_error(self, mock_available):
        """Test error handling for workspace count."""
        mock_available.return_value = False
        with patch("src.workspace.manager._gdbus_workspace_call") as mock_gdbus:
            mock_gdbus.return_value = (False, "error")
            result = get_workspace_count(dev_mode=False)
            assert result == 1


class TestEnsureExtension:
    """Test ensure_extension function."""

    def test_ensure_extension_dev_mode(self):
        """Test ensure extension in dev mode."""
        ok, msg = ensure_extension(dev_mode=True)
        assert ok is True
        assert "DEV" in msg

    @patch("src.workspace.manager._is_extension_enabled")
    @patch("os.path.exists")
    def test_ensure_extension_already_installed(self, mock_exists, mock_enabled):
        """Test when extension is already installed but not enabled."""
        def exists_side_effect(path):
            return "sessionintent" in str(path)
        mock_exists.side_effect = exists_side_effect
        mock_enabled.return_value = False
        with patch("src.workspace.manager._enable_extension") as mock_enable:
            mock_enable.return_value = (True, "Enabled")
            ok, msg = ensure_extension(dev_mode=False)
            assert ok is True
            assert "Restart GNOME Shell" in msg

    @patch("src.workspace.manager._is_extension_enabled")
    @patch("src.workspace.manager._enable_extension")
    @patch("os.path.exists")
    def test_ensure_extension_enable_fails(self, mock_exists, mock_enable, mock_enabled):
        """Test when enabling the extension fails."""
        def exists_side_effect(path):
            path_str = str(path)
            if "sessionintent" in path_str and "~" in path_str:
                return True
            if "sessionintent" in path_str and "extensions/sessionintent" in path_str:
                return True
            return True
        mock_exists.side_effect = exists_side_effect
        mock_enabled.return_value = False
        mock_enable.return_value = (False, "Failed to enable extension")
        ok, msg = ensure_extension(dev_mode=False)
        assert ok is False
        assert "Failed to enable" in msg

    @patch("src.workspace.manager._is_extension_enabled")
    @patch("os.path.exists")
    def test_ensure_extension_already_enabled(self, mock_exists, mock_enabled):
        """Test when extension is already enabled."""
        def exists_side_effect(path):
            return "sessionintent" in str(path)
        mock_exists.side_effect = exists_side_effect
        mock_enabled.return_value = True
        ok, msg = ensure_extension(dev_mode=False)
        assert ok is True
        assert "already enabled" in msg