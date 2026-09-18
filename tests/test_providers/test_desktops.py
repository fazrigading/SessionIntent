"""Tests for KDE/Hyprland/Sway/wlroots providers, detection, and --backend."""

from unittest.mock import MagicMock, patch

from sessionintent.cli.parser import parse_args
from sessionintent.providers import detect_desktop, get_providers
from sessionintent.providers.display.tui import TuiDisplayProvider
from sessionintent.providers.extensions.kde import KdeExtensionProvider
from sessionintent.providers.workspace.hyprland import HyprlandWorkspaceProvider
from sessionintent.providers.workspace.kde import KdeWorkspaceProvider
from sessionintent.providers.workspace.sway import SwayWorkspaceProvider
from sessionintent.providers.workspace.wlroots import WlrootsWorkspaceProvider


def _result(stdout="", returncode=0):
    mock = MagicMock()
    mock.stdout = stdout
    mock.returncode = returncode
    return mock


def _env(**overrides):
    base: dict[str, str] = {}
    base.update(overrides)
    return base


class TestKdeWorkspace:
    @patch("subprocess.run")
    def test_switch(self, mock_run):
        mock_run.return_value = _result()
        assert KdeWorkspaceProvider().switch_workspace(3) is True
        args = mock_run.call_args[0][0]
        assert args[:4] == ["qdbus", "org.kde.KWin", "/KWin", "setCurrentDesktop"]
        assert args[4] == "3"

    @patch("subprocess.run")
    def test_current(self, mock_run):
        mock_run.return_value = _result("2\n")
        assert KdeWorkspaceProvider().get_current_workspace() == 2

    @patch("subprocess.run")
    def test_count(self, mock_run):
        mock_run.return_value = _result("4\n")
        assert KdeWorkspaceProvider().get_workspace_count() == 4

    @patch("subprocess.run")
    def test_tool_missing(self, mock_run):
        mock_run.side_effect = FileNotFoundError
        provider = KdeWorkspaceProvider()
        assert provider.switch_workspace(1) is False
        assert provider.get_current_workspace() is None

    def test_dev_mode(self):
        provider = KdeWorkspaceProvider(dev_mode=True)
        assert provider.switch_workspace(1) is True
        assert provider.get_current_workspace() == 1


class TestHyprlandWorkspace:
    @patch("subprocess.run")
    def test_switch(self, mock_run):
        mock_run.return_value = _result()
        assert HyprlandWorkspaceProvider().switch_workspace(2) is True
        assert mock_run.call_args[0][0] == [
            "hyprctl",
            "dispatch",
            "workspace",
            "2",
        ]

    @patch("subprocess.run")
    def test_current(self, mock_run):
        mock_run.return_value = _result('{"id": 3, "name": "3"}')
        assert HyprlandWorkspaceProvider().get_current_workspace() == 3

    @patch("subprocess.run")
    def test_count(self, mock_run):
        mock_run.return_value = _result('[{"id": 1}, {"id": 2}]')
        assert HyprlandWorkspaceProvider().get_workspace_count() == 2

    @patch("subprocess.run")
    def test_bad_json(self, mock_run):
        mock_run.return_value = _result("not json")
        provider = HyprlandWorkspaceProvider()
        assert provider.get_current_workspace() is None
        assert provider.get_workspace_count() == 1


class TestSwayWorkspace:
    @patch("subprocess.run")
    def test_switch(self, mock_run):
        mock_run.return_value = _result('[{"success": true}]')
        assert SwayWorkspaceProvider().switch_workspace(2) is True
        assert mock_run.call_args[0][0] == ["swaymsg", "workspace", "number", "2"]

    @patch("subprocess.run")
    def test_current_focused(self, mock_run):
        mock_run.return_value = _result('[{"num": 1}, {"num": 2, "focused": true}]')
        assert SwayWorkspaceProvider().get_current_workspace() == 2

    @patch("subprocess.run")
    def test_count(self, mock_run):
        mock_run.return_value = _result('[{"num": 1}, {"num": 2}]')
        assert SwayWorkspaceProvider().get_workspace_count() == 2


class TestWlrootsChain:
    @patch("shutil.which")
    def test_prefers_hyprland(self, mock_which):
        mock_which.side_effect = lambda tool: "/usr/bin/" + tool if tool == "hyprctl" else None
        provider = WlrootsWorkspaceProvider(dev_mode=True)
        assert isinstance(provider._inner, HyprlandWorkspaceProvider)

    @patch("shutil.which")
    def test_falls_back_to_sway(self, mock_which):
        mock_which.side_effect = lambda tool: "/usr/bin/" + tool if tool == "swaymsg" else None
        provider = WlrootsWorkspaceProvider(dev_mode=True)
        assert isinstance(provider._inner, SwayWorkspaceProvider)

    @patch("shutil.which")
    def test_falls_back_to_ewmh(self, mock_which):
        mock_which.return_value = None
        provider = WlrootsWorkspaceProvider(dev_mode=True)
        assert provider.switch_workspace(1) is True


class TestKdeExtensions:
    @patch("sessionintent.providers.extensions.kde._kpackagetool")
    @patch("sessionintent.providers.extensions.kde._run")
    def test_list(self, mock_run, mock_tool):
        mock_tool.return_value = "kpackagetool6"
        mock_run.return_value = "org.kde.plasma.systemmonitor\norg.kde.plasma.clock\n"
        assert KdeExtensionProvider().list() == [
            "org.kde.plasma.systemmonitor",
            "org.kde.plasma.clock",
        ]

    def test_enable_reports_manual_step(self):
        ok, msg = KdeExtensionProvider().enable("org.kde.plasma.clock")
        assert ok is False
        assert "manually" in msg

    def test_dev_mode(self):
        provider = KdeExtensionProvider(dev_mode=True)
        assert provider.list() != []
        assert provider.ensure()[0] is True


class TestDesktopDetection:
    def test_wlroots_generic(self):
        profile = detect_desktop(
            _env(XDG_SESSION_TYPE="wayland", WAYLAND_DISPLAY="wayland-1")
        )
        assert profile.desktop == "wlroots"

    def test_gnome_not_overridden_by_wayland_display(self):
        profile = detect_desktop(
            _env(
                XDG_SESSION_TYPE="wayland",
                DESKTOP_SESSION="gnome",
                WAYLAND_DISPLAY="wayland-0",
            )
        )
        assert profile.desktop == "gnome"

    def test_kde_capabilities(self):
        profile = detect_desktop(_env(KDE_FULL_SESSION="true"))
        assert "extensions" in profile.capabilities


class TestDesktopFactory:
    def test_kde_providers(self):
        ws, _, ext = get_providers(
            detect_desktop(_env(KDE_FULL_SESSION="true")), dev_mode=True
        )
        assert isinstance(ws, KdeWorkspaceProvider)
        assert isinstance(ext, KdeExtensionProvider)

    def test_hyprland_providers(self):
        ws, _, _ = get_providers(
            detect_desktop(_env(HYPRLAND_INSTANCE_SIGNATURE="sig")), dev_mode=True
        )
        assert isinstance(ws, HyprlandWorkspaceProvider)

    def test_sway_providers(self):
        ws, _, _ = get_providers(
            detect_desktop(_env(SWAYSOCK="/run/sway-ipc")), dev_mode=True
        )
        assert isinstance(ws, SwayWorkspaceProvider)

    def test_wlroots_providers(self):
        ws, _, _ = get_providers(
            detect_desktop(_env(XDG_SESSION_TYPE="wayland", WAYLAND_DISPLAY="wl-1")),
            dev_mode=True,
        )
        assert isinstance(ws, WlrootsWorkspaceProvider)

    def test_backend_override(self):
        ws, _, _ = get_providers(
            detect_desktop(_env(DESKTOP_SESSION="gnome")),
            dev_mode=True,
            backend="sway",
        )
        assert isinstance(ws, SwayWorkspaceProvider)


class TestBackendFlag:
    def test_backend_parsed(self):
        assert parse_args(["--backend", "kde"]).backend == "kde"

    def test_backend_default_none(self):
        assert parse_args([]).backend is None

    def test_tui_fallback_without_selector_tools(self):
        profile = detect_desktop(_env())
        profile.tool_availability = {}
        _, display, _ = get_providers(profile, dev_mode=True)
        assert isinstance(display, TuiDisplayProvider)
