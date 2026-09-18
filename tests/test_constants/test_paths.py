"""Tests for constants package."""

from pathlib import Path

from sessionintent.constants.paths import (
    CONFIG_DIR,
    STATE_DIR,
    CONFIG_PATH,
    APPS_PATH,
    STATE_FILE,
    AC_PATH,
)


class TestPaths:
    """Test path constants."""

    def test_config_dir_exists(self):
        """Test CONFIG_DIR is a Path object."""
        assert isinstance(CONFIG_DIR, Path)

    def test_config_path_is_correct(self):
        """Test CONFIG_PATH points to config.yaml."""
        assert CONFIG_PATH.name == "config.yaml"
        assert CONFIG_PATH.parent == CONFIG_DIR

    def test_apps_path_is_correct(self):
        """Test APPS_PATH points to apps.yaml."""
        assert APPS_PATH.name == "apps.yaml"
        assert APPS_PATH.parent == CONFIG_DIR

    def test_state_file_includes_current(self):
        """Test STATE_FILE includes current file."""
        assert STATE_FILE.name == "current"
        assert STATE_FILE.parent == STATE_DIR

    def test_ac_path_is_correct(self):
        """Test AC_PATH points to correct system path."""
        assert AC_PATH == "/sys/class/power_supply/AC/online"


class TestXdgCompliance:
    """Test XDG base directory resolution."""

    def _reload_paths(self, monkeypatch, **env):
        import importlib

        import sessionintent.constants.paths as paths

        for key in ("XDG_CONFIG_HOME", "XDG_STATE_HOME"):
            monkeypatch.delenv(key, raising=False)
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        return importlib.reload(paths)

    def test_config_home_override(self, monkeypatch, tmp_path):
        paths = self._reload_paths(monkeypatch, XDG_CONFIG_HOME=str(tmp_path))
        try:
            assert paths.CONFIG_DIR == tmp_path / "sessionintent"
            assert paths.CONFIG_PATH.parent == paths.CONFIG_DIR
        finally:
            import importlib

            importlib.reload(paths)

    def test_state_home_override(self, monkeypatch, tmp_path):
        paths = self._reload_paths(monkeypatch, XDG_STATE_HOME=str(tmp_path))
        try:
            assert paths.STATE_DIR == tmp_path / "sessionintent"
        finally:
            import importlib

            importlib.reload(paths)

    def test_empty_counts_as_unset(self, monkeypatch):
        paths = self._reload_paths(
            monkeypatch, XDG_CONFIG_HOME="", XDG_STATE_HOME=""
        )
        try:
            assert ".config" in paths.CONFIG_DIR.parts
            assert ".local" in paths.STATE_DIR.parts
        finally:
            import importlib

            importlib.reload(paths)


class TestDefaults:
    """Test default values."""

    def test_default_apps_is_string(self):
        """Test DEFAULT_APPS is a string."""
        from sessionintent.constants.defaults import DEFAULT_APPS

        assert isinstance(DEFAULT_APPS, str)
        assert "firefox" in DEFAULT_APPS
        assert "vscode" in DEFAULT_APPS

    def test_default_config_is_string(self):
        """Test DEFAULT_CONFIG is a string."""
        from sessionintent.constants.defaults import DEFAULT_CONFIG

        assert isinstance(DEFAULT_CONFIG, str)
        assert "modes" in DEFAULT_CONFIG
        assert "browsing" in DEFAULT_CONFIG
