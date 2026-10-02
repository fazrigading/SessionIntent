"""Tests for workspace manager."""

import json
import os
from unittest.mock import patch, MagicMock
import subprocess

from sessionintent.providers.workspace.gnome import (
    GnomeWorkspaceProvider,
    switch_workspace,
    get_current_workspace,
    get_workspace_count,
    ensure_extension,
    wait_for_workspace,
    _extension_needs_update,
    _extension_source_dir,
    _list_windows,
    _socket_call,
    _is_extension_available,
    _gdbus_workspace_call,
    _window_matches,
    wait_for_window as gnome_wait_for_window,
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

    

    @patch("sessionintent.providers.workspace.gnome._get_socket_path")
    def test_socket_call_no_runtime_dir(self, mock_get_path):
        """Test socket call when XDG_RUNTIME_DIR not set."""
        mock_get_path.return_value = None
        ok, resp = _socket_call("CURRENT\n")
        assert ok is False
        assert "XDG_RUNTIME_DIR" in resp

    @patch("sessionintent.providers.workspace.gnome._get_socket_path")
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

    @patch("sessionintent.providers.workspace.gnome._socket_call")
    def test_socket_available(self, mock_socket_call):
        """Test when socket is available."""
        mock_socket_call.return_value = (True, "0")
        assert _is_extension_available(dev_mode=False) is True

    @patch("sessionintent.providers.workspace.gnome._socket_call")
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

    @patch("sessionintent.providers.workspace.gnome.subprocess.run")
    def test_real_mode_failure(self, mock_run):
        """Test failed gdbus call."""
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        ok, resp = _gdbus_workspace_call("Main.wm.get_active_workspace_index()", dev_mode=False)
        assert ok is False

    @patch("sessionintent.providers.workspace.gnome.subprocess.run")
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

    @patch("sessionintent.providers.workspace.gnome._is_extension_available")
    def test_switch_workspace_socket_success(self, mock_available):
        """Test switching via socket."""
        mock_available.return_value = True
        with patch("sessionintent.providers.workspace.gnome._socket_call") as mock_call:
            mock_call.return_value = (True, "OK")
            result = switch_workspace(3, dev_mode=False)
            assert result is True
            mock_call.assert_called_once()
            assert "SWITCH 2" in mock_call.call_args[0][0]

    @patch("sessionintent.providers.workspace.gnome._is_extension_available")
    def test_switch_workspace_socket_with_monitor(self, mock_available):
        """Test switching via socket with monitor."""
        mock_available.return_value = True
        with patch("sessionintent.providers.workspace.gnome._socket_call") as mock_call:
            mock_call.return_value = (True, "OK")
            result = switch_workspace(2, dev_mode=False, monitor="DP-1")
            assert result is True
            call_str = mock_call.call_args[0][0]
            assert "SWITCH 1" in call_str
            assert "DP-1" in call_str

    @patch("sessionintent.providers.workspace.gnome._is_extension_available")
    def test_switch_workspace_gdbus_fallback(self, mock_available):
        """Test gdbus fallback when socket unavailable."""
        mock_available.return_value = False
        with patch("sessionintent.providers.workspace.gnome._gdbus_workspace_call") as mock_gdbus:
            with patch("time.sleep"):
                mock_gdbus.return_value = (True, "(true, '')")
                result = switch_workspace(2, dev_mode=False)
                assert result is True
                mock_gdbus.assert_called_once()

    @patch("sessionintent.providers.workspace.gnome._is_extension_available")
    def test_switch_workspace_all_methods_fail(self, mock_available):
        """Test failure when both socket and gdbus fail."""
        mock_available.return_value = False
        with patch("sessionintent.providers.workspace.gnome._gdbus_workspace_call") as mock_gdbus:
            mock_gdbus.return_value = (False, "error")
            result = switch_workspace(1, dev_mode=False)
            assert result is False


class TestWaitForWorkspace:
    """Test wait_for_workspace function."""

    def test_wait_dev_mode(self):
        """Test wait in dev mode returns immediately."""
        assert wait_for_workspace(1, dev_mode=True) is True

    @patch("sessionintent.providers.workspace.gnome.get_current_workspace")
    def test_wait_success(self, mock_current):
        """Test successful wait."""
        mock_current.side_effect = [1, 2, 3]
        result = wait_for_workspace(2, dev_mode=False, timeout=1.0)
        assert result is True
        assert mock_current.call_count == 2

    @patch("sessionintent.providers.workspace.gnome.get_current_workspace")
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

    @patch("sessionintent.providers.workspace.gnome._is_extension_available")
    def test_get_current_workspace_socket(self, mock_available):
        """Test getting current workspace via socket."""
        mock_available.return_value = True
        with patch("sessionintent.providers.workspace.gnome._socket_call") as mock_call:
            mock_call.return_value = (True, "2")
            result = get_current_workspace(dev_mode=False)
            assert result == 3

    @patch("sessionintent.providers.workspace.gnome._is_extension_available")
    def test_get_current_workspace_gdbus_fallback(self, mock_available):
        """Test getting current workspace via gdbus."""
        mock_available.return_value = False
        with patch("sessionintent.providers.workspace.gnome._gdbus_workspace_call") as mock_gdbus:
            mock_gdbus.return_value = (True, "(uint32 2,)")
            result = get_current_workspace(dev_mode=False)
            assert result == 3

    @patch("sessionintent.providers.workspace.gnome._is_extension_available")
    def test_get_current_workspace_no_gnome(self, mock_available):
        """Test getting current workspace when GNOME not available."""
        mock_available.return_value = False
        with patch("sessionintent.providers.workspace.gnome._gdbus_workspace_call") as mock_gdbus:
            mock_gdbus.return_value = (False, "error")
            result = get_current_workspace(dev_mode=False)
            assert result is None


class TestGetWorkspaceCount:
    """Test get_workspace_count function."""

    def test_get_workspace_count_dev_mode(self):
        """Test getting workspace count in dev mode."""
        result = get_workspace_count(dev_mode=True)
        assert result == 1

    @patch("sessionintent.providers.workspace.gnome._is_extension_available")
    def test_get_workspace_count_socket(self, mock_available):
        """Test getting workspace count via socket."""
        mock_available.return_value = True
        with patch("sessionintent.providers.workspace.gnome._socket_call") as mock_call:
            mock_call.return_value = (True, "4")
            result = get_workspace_count(dev_mode=False)
            assert result == 4

    @patch("sessionintent.providers.workspace.gnome._is_extension_available")
    def test_get_workspace_count_gdbus_fallback(self, mock_available):
        """Test getting workspace count via gdbus."""
        mock_available.return_value = False
        with patch("sessionintent.providers.workspace.gnome._gdbus_workspace_call") as mock_gdbus:
            mock_gdbus.return_value = (True, "(uint32 3,)")
            result = get_workspace_count(dev_mode=False)
            assert result == 3

    @patch("sessionintent.providers.workspace.gnome._is_extension_available")
    def test_get_workspace_count_error(self, mock_available):
        """Test error handling for workspace count."""
        mock_available.return_value = False
        with patch("sessionintent.providers.workspace.gnome._gdbus_workspace_call") as mock_gdbus:
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

    @patch("sessionintent.providers.workspace.gnome._is_extension_enabled")
    @patch("os.path.exists")
    def test_ensure_extension_already_installed(self, mock_exists, mock_enabled):
        """Test when extension is already installed but not enabled."""
        def exists_side_effect(path):
            return "sessionintent" in str(path)
        mock_exists.side_effect = exists_side_effect
        mock_enabled.return_value = False
        with patch("sessionintent.providers.workspace.gnome._enable_extension") as mock_enable:
            mock_enable.return_value = (True, "Enabled")
            ok, msg = ensure_extension(dev_mode=False)
            assert ok is True
            assert "Restart GNOME Shell" in msg

    @patch("sessionintent.providers.workspace.gnome._is_extension_enabled")
    @patch("sessionintent.providers.workspace.gnome._enable_extension")
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

    @patch("sessionintent.providers.workspace.gnome._is_extension_enabled")
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


def _write_metadata(path, version, shells):
    path.mkdir(parents=True, exist_ok=True)
    (path / "metadata.json").write_text(
        json.dumps({"version": version, "shell-version": shells})
    )
    (path / "extension.js").write_text("// stub")


class TestExtensionUpdate:
    """Test stale-install detection and reinstall."""

    def test_source_dir_finds_repo_metadata(self):
        src = _extension_source_dir()
        assert src is not None
        assert src.endswith(os.path.join("extensions", "sessionintent-ws"))

    def test_needs_update_on_version_bump(self, tmp_path):
        installed = tmp_path / "inst"
        source = tmp_path / "src"
        _write_metadata(installed, 1, ["49"])
        _write_metadata(source, 2, ["49", "50", "51"])
        assert _extension_needs_update(str(installed), str(source)) is True
        assert _extension_needs_update(str(source), str(source)) is False

    def test_ensure_reinstalls_stale_install(self, tmp_path, monkeypatch):
        """Stale v1 install + v2 source -> reinstall, report updated."""
        monkeypatch.setenv("HOME", str(tmp_path))
        ext_dir = (
            tmp_path
            / ".local/share/gnome-shell/extensions"
            / "sessionintent-ws@fazrigading.github.io"
        )
        source = tmp_path / "source"
        _write_metadata(ext_dir, 1, ["49"])
        _write_metadata(source, 2, ["49", "50", "51"])
        with (
            patch(
                "sessionintent.providers.workspace.gnome._extension_source_dir",
                return_value=str(source),
            ),
            patch(
                "sessionintent.providers.workspace.gnome._is_extension_enabled",
                return_value=True,
            ),
        ):
            ok, msg = ensure_extension(dev_mode=False)
        assert ok is True
        assert "updated" in msg
        assert json.loads((ext_dir / "metadata.json").read_text())["version"] == 2


_FF_ROW = {
    "ws": 0,
    "appId": "org.mozilla.firefox",
    "sandboxId": "",
    "class": "firefox",
    "title": "New Tab",
    "pid": 123,
}
_LIST_JSON = json.dumps([_FF_ROW])


class TestWindowMatches:
    """Test _window_matches precedence and case handling."""

    def test_app_id_match(self):
        assert _window_matches(_FF_ROW, "firefox") is True

    def test_sandbox_id_match(self):
        row = dict(_FF_ROW, appId="", sandboxId="com.rtosta.zapzap", **{"class": ""})
        assert _window_matches(row, "zapzap") is True

    def test_case_insensitive(self):
        assert _window_matches(_FF_ROW, "FireFox") is True

    def test_title_fallback(self):
        row = dict(_FF_ROW, appId="", sandboxId="", **{"class": ""})
        assert _window_matches(row, "new tab") is True

    def test_no_match(self):
        assert _window_matches(_FF_ROW, "discord") is False


class TestListWindows:
    """Test _list_windows parsing and status reporting."""

    def test_ok(self):
        with (
            patch(
                "sessionintent.providers.workspace.gnome._is_extension_available",
                return_value=True,
            ),
            patch(
                "sessionintent.providers.workspace.gnome._socket_call",
                return_value=(True, _LIST_JSON),
            ),
        ):
            windows, status = _list_windows(dev_mode=False)
        assert status == "ok"
        assert windows[0]["appId"] == "org.mozilla.firefox"

    def test_unavailable_no_socket(self):
        with patch(
            "sessionintent.providers.workspace.gnome._is_extension_available",
            return_value=False,
        ):
            assert _list_windows(dev_mode=False) == ([], "unavailable")

    def test_unsupported_old_extension(self):
        with (
            patch(
                "sessionintent.providers.workspace.gnome._is_extension_available",
                return_value=True,
            ),
            patch(
                "sessionintent.providers.workspace.gnome._socket_call",
                return_value=(True, "ERR: unknown command 'LIST'"),
            ),
        ):
            assert _list_windows(dev_mode=False) == ([], "unsupported")

    def test_malformed_json(self):
        with (
            patch(
                "sessionintent.providers.workspace.gnome._is_extension_available",
                return_value=True,
            ),
            patch(
                "sessionintent.providers.workspace.gnome._socket_call",
                return_value=(True, "not json"),
            ),
        ):
            assert _list_windows(dev_mode=False) == ([], "unavailable")


class TestGnomeWaitForWindow:
    """Test socket-based wait_for_window."""

    def test_dev_mode(self):
        assert gnome_wait_for_window("x", 1, dev_mode=True) is True

    def test_found_on_target(self):
        with patch(
            "sessionintent.providers.workspace.gnome._list_windows",
            side_effect=[([], "ok"), ([_FF_ROW], "ok")],
        ):
            assert gnome_wait_for_window("firefox", 1, timeout=2.0) is True

    def test_wrong_workspace_ignored(self):
        row = dict(_FF_ROW, ws=1)
        with patch(
            "sessionintent.providers.workspace.gnome._list_windows",
            return_value=([row], "ok"),
        ):
            assert gnome_wait_for_window("firefox", 1, timeout=0.2) is False

    def test_unsupported_warns_once_and_fails(self, capsys, monkeypatch):
        import sessionintent.providers.workspace.gnome as gnomemod

        monkeypatch.setattr(gnomemod, "_warned_list_unsupported", False)
        with patch(
            "sessionintent.providers.workspace.gnome._list_windows",
            return_value=([], "unsupported"),
        ):
            assert gnome_wait_for_window("x", 1) is False
            assert gnome_wait_for_window("x", 1) is False
        assert capsys.readouterr().out.count("too old for window tracking") == 1

    def test_unavailable_fails_fast(self):
        with patch(
            "sessionintent.providers.workspace.gnome._list_windows",
            return_value=([], "unavailable"),
        ):
            assert gnome_wait_for_window("x", 1, timeout=15.0) is False


class TestProviderWaitFallback:
    """Test GnomeWorkspaceProvider falls back to ewmh."""

    def test_socket_wait_wins(self):
        provider = GnomeWorkspaceProvider(dev_mode=True)
        with patch(
            "sessionintent.providers.workspace.gnome.wait_for_window",
            return_value=True,
        ) as mock_socket:
            assert provider.wait_for_window("x", 1) is True
            mock_socket.assert_called_once()

    def test_ewmh_fallback(self):
        provider = GnomeWorkspaceProvider(dev_mode=True)
        with (
            patch(
                "sessionintent.providers.workspace.gnome.wait_for_window",
                return_value=False,
            ),
            patch(
                "sessionintent.providers.workspace.ewmh.EwmhWorkspaceProvider"
                ".wait_for_window",
                return_value=True,
            ),
        ):
            assert provider.wait_for_window("x", 1) is True