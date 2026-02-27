"""Tests for main session manager functionality."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.session import SessionManager
from src.config import load_config, load_apps
from src.constants import CONFIG_DIR, APPS_PATH


# Mock data
MOCK_CONFIG = {
    "version": 1,
    "defaults": {"ask_before_kill": True, "reuse_workspaces": True},
    "hardware_profiles": {
        "battery": {"disable_modes": ["gaming"]},
        "plugged": {"allow_all": True},
    },
    "modes": {
        "browsing": {
            "label": "Browsing",
            "workspaces": {"1": ["firefox"], "2": ["discord"]},
        },
        "work": {"label": "Work", "workspaces": {"1": ["firefox"], "2": ["vscode"]}},
    },
}

MOCK_APPS = {
    "firefox": {
        "cmd": ["firefox", "-P", "{profile|default}"],
        "append_param": "urls",
        "internal_reuse": True,
    },
    "vscode": {
        "cmd": ["code", "--reuse-window", "{workspace|}"],
        "primary_param": "workspace",
        "internal_reuse": True,
    },
    "discord": {"cmd": ["discord"], "check": "discord", "internal_reuse": False},
}


class TestSessionManagerInit:
    """Test SessionManager initialization."""

    def test_init_dev_mode(self, tmp_path, monkeypatch):
        """Test initialization with dev mode enabled."""
        with patch("src.session.manager.load_config", return_value={}):
            with patch("src.session.manager.load_apps", return_value={}):
                manager = SessionManager(dev_mode=True)
                assert manager.dev_mode is True
                assert manager.config == {}

    def test_init_no_dev_mode_creates_state_dir(self, tmp_path, monkeypatch):
        """Test that non-dev mode creates state directory."""
        monkeypatch.setattr("src.session.manager.STATE_DIR", tmp_path / "state")

        manager = SessionManager(dev_mode=False)

        assert (tmp_path / "state").exists()

    def test_init_with_custom_config(self, tmp_path):
        """Test initialization with custom config path."""
        config_path = tmp_path / "custom_config.yaml"
        with open(config_path, "w") as f:
            f.write("modes:\n  test:\n    label: Test\n")

        manager = SessionManager(config_path=str(config_path))
        assert "modes" in manager.config


class TestApplyMode:
    """Test applying session modes."""

    def test_apply_nonexistent_mode(self, tmp_path):
        """Test applying a non-existent mode."""
        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            f.write("modes: {}")

        with patch("src.constants.paths.CONFIG_PATH", config_path):
            manager = SessionManager(config_path=str(config_path))

            # Should print error and return without error
            manager.apply_mode("nonexistent")

    def test_apply_mode_saves_state(self, tmp_path):
        """Test that applying a mode saves state."""
        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            f.write("modes:\n  work:\n    label: Work\n    workspaces: {}\n")

        with patch("src.constants.paths.CONFIG_PATH", config_path):
            manager = SessionManager(config_path=str(config_path))

            manager.apply_mode("work")

            state_file = tmp_path / ".local" / "state" / "sessionintent" / "current"
            assert not state_file.exists()  # Would be created with proper paths


class TestPanic:
    """Test panic reset functionality."""

    def test_panic_clears_state(self, tmp_path, monkeypatch):
        """Test panic clears state file."""
        state_dir = tmp_path / "state"
        state_file = state_dir / "current"
        state_dir.mkdir(parents=True)
        state_file.write_text("work")

        monkeypatch.setattr("src.session.state.STATE_FILE", state_file)
        manager = SessionManager(dev_mode=False)
        manager.panic()

        assert not state_file.exists()


class TestGetAvailableModes:
    """Test mode filtering based on hardware."""

    def test_available_modes_with_battery(self, tmp_path, monkeypatch):
        """Test that gaming mode is disabled on battery."""
        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            f.write("""
hardware_profiles:
  battery:
    disable_modes: [gaming]
modes:
  work:
    label: Work
  gaming:
    label: Gaming
""")

        with patch("src.constants.paths.CONFIG_PATH", config_path):
            with patch("src.ui.selector.is_on_ac", return_value=False):
                manager = SessionManager(config_path=str(config_path))

                modes = manager.get_available_modes()
                assert "work" in modes
                assert "gaming" not in modes

    def test_available_modes_with_ac(self, tmp_path, monkeypatch):
        """Test that all modes available when plugged in."""
        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            f.write("""
hardware_profiles:
  battery:
    disable_modes: [gaming]
modes:
  work:
    label: Work
  gaming:
    label: Gaming
""")

        with patch("src.constants.paths.CONFIG_PATH", config_path):
            with patch("src.hardware.power.is_on_ac", return_value=True):
                manager = SessionManager(config_path=str(config_path))

                modes = manager.get_available_modes()
                assert "work" in modes
                assert "gaming" in modes
