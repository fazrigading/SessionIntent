"""Tests for desktop detection, provider factory, and TUI fallback."""

import pytest

from sessionintent.providers import ProviderError, detect_desktop, get_providers
from sessionintent.providers.display.tui import TuiDisplayProvider
from sessionintent.providers.extensions.gnome import NullExtensionProvider
from sessionintent.providers.workspace.ewmh import EwmhWorkspaceProvider
from sessionintent.providers.workspace.gnome import GnomeWorkspaceProvider


def _env(**overrides):
    base = {k: v for k, v in {}.items()}
    base.update(overrides)
    return base


class TestDetectDesktop:
    def test_gnome_wayland(self):
        profile = detect_desktop(_env(XDG_SESSION_TYPE="wayland", DESKTOP_SESSION="gnome"))
        assert profile.desktop == "gnome"
        assert profile.wm_type == "mutter"
        assert "workspace" in profile.capabilities

    def test_hyprland_signature_overrides(self):
        profile = detect_desktop(
            _env(DESKTOP_SESSION="hyprland", HYPRLAND_INSTANCE_SIGNATURE="abc123")
        )
        assert profile.desktop == "hyprland"

    def test_sway_socket(self):
        profile = detect_desktop(_env(SWAYSOCK="/run/user/1000/sway-ipc.sock"))
        assert profile.desktop == "sway"

    def test_kde_session(self):
        profile = detect_desktop(_env(KDE_FULL_SESSION="true"))
        assert profile.desktop == "kde"
        assert profile.wm_type == "kwin"

    def test_unknown_defaults(self):
        profile = detect_desktop(_env())
        assert profile.desktop == "unknown"
        assert profile.session_type == "unknown"


class TestGetProviders:
    def test_gnome_default(self):
        profile = detect_desktop(_env(DESKTOP_SESSION="gnome"))
        ws, display, ext = get_providers(profile, dev_mode=True)
        assert isinstance(ws, GnomeWorkspaceProvider)
        assert display is not None
        assert ext is not None

    def test_unknown_desktop_preserves_gnome_behavior(self):
        ws, _, _ = get_providers(detect_desktop(_env()), dev_mode=True)
        assert isinstance(ws, GnomeWorkspaceProvider)

    def test_ewmh_backend_override(self):
        ws, _, _ = get_providers(
            detect_desktop(_env(DESKTOP_SESSION="gnome")),
            dev_mode=True,
            backend="ewmh",
        )
        assert isinstance(ws, EwmhWorkspaceProvider)

    def test_non_gnome_gets_null_extensions(self):
        _, _, ext = get_providers(
            detect_desktop(_env(DESKTOP_SESSION="i3")), dev_mode=True
        )
        assert isinstance(ext, NullExtensionProvider)
        assert ext.apply({}) != []

    def test_unknown_backend_raises(self):
        with pytest.raises(ProviderError):
            get_providers(detect_desktop(_env()), dev_mode=True, backend="bspwm")


class TestTuiDisplay:
    def test_select_by_number(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "2")
        modes = {"a": {"label": "A"}, "b": {"label": "B"}}
        assert TuiDisplayProvider().select_mode(modes) == "b"

    def test_select_empty_returns_none(self):
        assert TuiDisplayProvider().select_mode({}) is None

    def test_select_eof_returns_none(self, monkeypatch):
        def boom(_):
            raise EOFError

        monkeypatch.setattr("builtins.input", boom)
        assert TuiDisplayProvider().select_mode({"a": {}}) is None

    def test_format_menu(self):
        entries = TuiDisplayProvider().format_menu({"a": {"label": "A"}})
        assert entries == ["1: A"]


class TestEwmhDevMode:
    def test_dev_mode_no_subprocess(self):
        provider = EwmhWorkspaceProvider(dev_mode=True)
        assert provider.switch_workspace(2) is True
        assert provider.get_current_workspace() == 1
        assert provider.get_workspace_count() == 1
        assert provider.wait_for_workspace(2) is True
        assert provider.wait_for_window("firefox", 1) is True
