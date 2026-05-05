"""Tests for main session manager functionality."""

from unittest.mock import patch

from src.session import SessionManager


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

        SessionManager(dev_mode=False)

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

    def test_apply_mode_saves_state(self, tmp_path, monkeypatch):
        """Test that applying a mode saves state."""
        state_file = tmp_path / "state" / "current"
        state_file.parent.mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr("src.session.state.STATE_FILE", state_file)

        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            f.write("modes:\n  work:\n    label: Work\n    workspaces: {}\n")

        with patch("src.constants.paths.CONFIG_PATH", config_path):
            manager = SessionManager(config_path=str(config_path), dev_mode=False)

            manager.apply_mode("work")

            assert state_file.exists()


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

    def test_panic_dev_mode(self, capsys):
        """Test panic in dev mode."""
        manager = SessionManager(dev_mode=True)
        manager.panic()
        captured = capsys.readouterr()
        assert "[DEV] Panic" in captured.out


class TestQuit:
    """Test quit functionality."""

    def test_quit_dev_mode(self, capsys):
        """Test quit in dev mode."""
        manager = SessionManager(dev_mode=True)
        manager.quit()
        captured = capsys.readouterr()
        assert "[DEV] Quit" in captured.out

    @patch("src.session.manager.SessionManager._get_managed_apps")
    @patch("src.session.manager.SessionManager._close_apps")
    def test_quit_with_apps(self, mock_close, mock_get_apps, tmp_path, monkeypatch):
        """Test quit closes managed apps."""
        mock_get_apps.return_value = ["firefox", "discord"]
        state_file = tmp_path / "state" / "current"
        state_file.parent.mkdir(parents=True)
        state_file.write_text("work")

        monkeypatch.setattr("src.session.state.STATE_FILE", state_file)

        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            f.write(
                "modes:\n  work:\n    label: Work\n    workspaces:\n      1: [firefox]\n"
            )

        with patch("src.constants.paths.CONFIG_PATH", config_path):
            manager = SessionManager(config_path=str(config_path), dev_mode=False)
            manager.quit()

        mock_close.assert_called_once_with(["firefox", "discord"], graceful=True)

    @patch("src.session.manager.SessionManager._get_managed_apps")
    def test_quit_no_apps(self, mock_get_apps, tmp_path, monkeypatch, capsys):
        """Test quit with no managed apps."""
        mock_get_apps.return_value = []
        state_file = tmp_path / "state" / "current"
        state_file.parent.mkdir(parents=True)
        state_file.write_text("work")

        monkeypatch.setattr("src.session.state.STATE_FILE", state_file)

        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            f.write("modes:\n  work:\n    label: Work\n")

        with patch("src.constants.paths.CONFIG_PATH", config_path):
            manager = SessionManager(config_path=str(config_path), dev_mode=False)
            manager.quit()

        captured = capsys.readouterr()
        assert "No managed applications" in captured.out

    def test_quit_no_active_mode(self, tmp_path, monkeypatch, capsys):
        """Test quit with no active mode."""
        state_file = tmp_path / "state" / "current"
        state_file.parent.mkdir(parents=True)

        monkeypatch.setattr("src.session.state.STATE_FILE", state_file)

        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            f.write("modes:\n  work:\n    label: Work\n")

        with patch("src.constants.paths.CONFIG_PATH", config_path):
            manager = SessionManager(config_path=str(config_path), dev_mode=False)
            manager.quit()

        captured = capsys.readouterr()
        assert "No active mode" in captured.out


class TestKill:
    """Test kill functionality."""

    def test_kill_dev_mode(self, capsys):
        """Test kill in dev mode."""
        manager = SessionManager(dev_mode=True)
        manager.kill()
        captured = capsys.readouterr()
        assert "[DEV] Kill" in captured.out

    @patch("src.session.manager.SessionManager._get_managed_apps")
    @patch("src.session.manager.SessionManager._close_apps")
    def test_kill_with_apps(self, mock_close, mock_get_apps, tmp_path, monkeypatch):
        """Test kill force kills managed apps."""
        mock_get_apps.return_value = ["firefox"]
        state_file = tmp_path / "state" / "current"
        state_file.parent.mkdir(parents=True)
        state_file.write_text("work")

        monkeypatch.setattr("src.session.state.STATE_FILE", state_file)

        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            f.write(
                "modes:\n  work:\n    label: Work\n    workspaces:\n      1: [firefox]\n"
            )

        with patch("src.constants.paths.CONFIG_PATH", config_path):
            manager = SessionManager(config_path=str(config_path), dev_mode=False)
            manager.kill()

        mock_close.assert_called_once_with(["firefox"], graceful=False)

    def test_kill_no_active_mode(self, tmp_path, monkeypatch, capsys):
        """Test kill with no active mode."""
        state_file = tmp_path / "state" / "current"
        state_file.parent.mkdir(parents=True)

        monkeypatch.setattr("src.session.state.STATE_FILE", state_file)

        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            f.write("modes:\n  work:\n    label: Work\n")

        with patch("src.constants.paths.CONFIG_PATH", config_path):
            manager = SessionManager(config_path=str(config_path), dev_mode=False)
            manager.kill()

        captured = capsys.readouterr()
        assert "No active mode" in captured.out


class TestClear:
    """Test clear functionality."""

    def test_clear_dev_mode(self, capsys):
        """Test clear in dev mode."""
        manager = SessionManager(dev_mode=True)
        manager.clear()
        captured = capsys.readouterr()
        assert "[DEV] Clear" in captured.out

    def test_clear_clears_state(self, tmp_path, monkeypatch):
        """Test clear removes state file."""
        state_dir = tmp_path / "state"
        state_file = state_dir / "current"
        state_dir.mkdir(parents=True)
        state_file.write_text("work")

        monkeypatch.setattr("src.session.state.STATE_FILE", state_file)
        manager = SessionManager(dev_mode=False)
        manager.clear()

        assert not state_file.exists()


class TestStatus:
    """Test status functionality."""

    def test_status_output(self, tmp_path, monkeypatch, capsys):
        """Test status shows correct information."""
        state_file = tmp_path / "state" / "current"
        state_file.parent.mkdir(parents=True)
        state_file.write_text("work")

        monkeypatch.setattr("src.session.state.STATE_FILE", state_file)

        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            f.write("modes:\n  work:\n    label: Work\n")

        with patch("src.constants.paths.CONFIG_PATH", config_path):
            with patch("src.hardware.power.is_on_ac", return_value=True):
                manager = SessionManager(config_path=str(config_path), dev_mode=False)
                manager.status()

        captured = capsys.readouterr()
        assert "SessionIntent Status" in captured.out
        assert "Current Mode: work" in captured.out
        assert "Power State: AC" in captured.out
        assert "Dev Mode: False" in captured.out


class TestListModes:
    """Test list_modes functionality."""

    def test_list_modes_with_disabled(self, tmp_path, monkeypatch, capsys):
        """Test list_modes shows disabled modes."""
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
            with patch("src.session.manager.is_on_ac", return_value=False):
                manager = SessionManager(config_path=str(config_path))
                manager.list_modes()

        captured = capsys.readouterr()
        assert "work" in captured.out
        assert "gaming" in captured.out
        assert "Disabled on battery" in captured.out
        assert "Disabled" in captured.out

    def test_list_modes_empty(self, tmp_path, monkeypatch, capsys):
        """Test list_modes with no modes defined."""
        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            f.write("modes: {}")

        with patch("src.constants.paths.CONFIG_PATH", config_path):
            manager = SessionManager(config_path=str(config_path))
            manager.list_modes()

        captured = capsys.readouterr()
        assert "No modes defined" in captured.out


class TestGetManagedApps:
    """Test _get_managed_apps private method."""

    def test_get_managed_apps_string(self, tmp_path):
        """Test _get_managed_apps with string entries."""
        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            f.write("modes:\n  work:\n    workspaces:\n      1: [firefox, discord]\n")

        manager = SessionManager(config_path=str(config_path), dev_mode=True)
        mode_cfg = manager.config.get("modes", {}).get("work", {})
        apps = manager._get_managed_apps(mode_cfg)

        assert "firefox" in apps
        assert "discord" in apps

    def test_get_managed_apps_dict(self, tmp_path):
        """Test _get_managed_apps with dict entries."""
        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            f.write(
                "modes:\n  work:\n    workspaces:\n      1:\n        - firefox:\n            profile: default\n"
            )

        manager = SessionManager(config_path=str(config_path), dev_mode=True)
        mode_cfg = manager.config.get("modes", {}).get("work", {})
        apps = manager._get_managed_apps(mode_cfg)

        assert "firefox" in apps


class TestReload:
    """Test reload functionality."""

    def test_reload_dev_mode(self, capsys):
        """Test reload in dev mode."""
        manager = SessionManager(dev_mode=True)
        manager.reload()
        captured = capsys.readouterr()
        assert "[DEV] Reload" in captured.out

    def test_reload_success(self, tmp_path, monkeypatch, capsys):
        """Test reload successfully reloads config."""
        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            f.write("modes:\n  work:\n    label: Work\n")

        monkeypatch.setattr("src.session.manager.CONFIG_PATH", config_path)
        manager = SessionManager(dev_mode=False)
        manager.reload()

        captured = capsys.readouterr()
        assert "Configuration reloaded" in captured.out


class TestSuspend:
    """Test suspend functionality."""

    def test_suspend_dev_mode(self, capsys):
        """Test suspend in dev mode."""
        manager = SessionManager(dev_mode=True)
        manager.suspend()
        captured = capsys.readouterr()
        assert "[DEV] Suspend" in captured.out

    def test_suspend_with_active_mode(self, tmp_path, monkeypatch, capsys):
        """Test suspend with active mode."""
        state_file = tmp_path / "state" / "current"
        state_file.parent.mkdir(parents=True)
        state_file.write_text("work")

        monkeypatch.setattr("src.session.state.STATE_FILE", state_file)

        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            f.write("modes:\n  work:\n    label: Work\n")

        with patch("src.constants.paths.CONFIG_PATH", config_path):
            manager = SessionManager(config_path=str(config_path), dev_mode=False)
            manager.suspend()

        captured = capsys.readouterr()
        assert "suspended" in captured.out.lower()

    def test_suspend_no_active_mode(self, tmp_path, monkeypatch, capsys):
        """Test suspend with no active mode."""
        state_file = tmp_path / "state" / "current"
        state_file.parent.mkdir(parents=True)

        monkeypatch.setattr("src.session.state.STATE_FILE", state_file)

        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            f.write("modes:\n  work:\n    label: Work\n")

        with patch("src.constants.paths.CONFIG_PATH", config_path):
            manager = SessionManager(config_path=str(config_path), dev_mode=False)
            manager.suspend()

        captured = capsys.readouterr()
        assert "No active mode" in captured.out


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
