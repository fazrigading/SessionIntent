"""Tests for config loader."""

import yaml
from pathlib import Path

from src.config.loader import (
    load_yaml_file,
    load_config,
    load_apps,
    init_default_configs,
)


class TestLoadYamlFile:
    """Test YAML file loading."""

    def test_load_nonexistent_file(self):
        """Test loading a non-existent file returns empty dict."""
        result = load_yaml_file(Path("/nonexistent/path.yaml"))
        assert result == {}

    def test_load_valid_yaml(self, tmp_path):
        """Test loading a valid YAML file."""
        test_file = tmp_path / "test.yaml"
        test_data = {"key": "value", "nested": {"inner": "data"}}
        with open(test_file, "w") as f:
            yaml.dump(test_data, f)

        result = load_yaml_file(test_file)
        assert result == test_data

    def test_load_empty_yaml(self, tmp_path):
        """Test loading an empty YAML file."""
        test_file = tmp_path / "empty.yaml"
        with open(test_file, "w") as f:
            f.write("")

        result = load_yaml_file(test_file)
        assert result == {}


class TestLoadConfig:
    """Test configuration loading."""

    def test_load_nonexistent_config(self, monkeypatch):
        """Test loading non-existent config returns empty dict."""
        # Monkeypatch to use temp dir
        monkeypatch.setattr(
            "src.config.loader.CONFIG_PATH", Path("/nonexistent/config.yaml")
        )
        result = load_config()
        assert result == {}

    def test_load_existing_config(self, tmp_path):
        """Test loading existing config file."""
        config_path = tmp_path / "config.yaml"
        test_data = {"modes": {"test": {"label": "Test"}}}
        with open(config_path, "w") as f:
            yaml.dump(test_data, f)

        result = load_config(str(config_path))
        assert result == test_data


class TestLoadApps:
    """Test app registry loading."""

    def test_load_empty_apps(self, tmp_path, monkeypatch):
        """Test loading when no apps files exist."""
        monkeypatch.setattr(
            "src.config.loader.SYSTEM_APPS_PATH", tmp_path / "system.yaml"
        )
        monkeypatch.setattr("src.config.loader.APPS_PATH", tmp_path / "user.yaml")

        result = load_apps()
        assert result == {}

    def test_load_user_apps_override(self, tmp_path, monkeypatch):
        """Test user apps override bundled apps."""
        system_path = tmp_path / "system.yaml"
        user_path = tmp_path / "user.yaml"

        with open(system_path, "w") as f:
            yaml.dump({"app1": {"cmd": ["app1"]}}, f)

        with open(user_path, "w") as f:
            yaml.dump({"app1": {"cmd": ["modified"]}, "app2": {"cmd": ["app2"]}}, f)

        monkeypatch.setattr("src.config.loader.SYSTEM_APPS_PATH", system_path)
        monkeypatch.setattr("src.config.loader.APPS_PATH", user_path)

        result = load_apps()
        # User should override bundled
        assert result["app1"]["cmd"] == ["modified"]
        assert result["app2"]["cmd"] == ["app2"]


class TestInitDefaultConfigs:
    """Test default config initialization."""

    def test_init_creates_config_directory(self, tmp_path, monkeypatch):
        """Test that initialization creates config directory."""
        config_dir = tmp_path / "config"
        config_path = config_dir / "config.yaml"
        apps_path = config_dir / "apps.yaml"

        monkeypatch.setattr("src.config.loader.CONFIG_DIR", config_dir)
        monkeypatch.setattr("src.config.loader.CONFIG_PATH", config_path)
        monkeypatch.setattr("src.config.loader.APPS_PATH", apps_path)

        init_default_configs()

        assert config_dir.exists()
        assert config_path.exists()
        assert apps_path.exists()

    def test_init_creates_default_content(self, tmp_path, monkeypatch):
        """Test that initialization creates default content."""
        config_dir = tmp_path / "config"
        config_path = config_dir / "config.yaml"
        apps_path = config_dir / "apps.yaml"

        monkeypatch.setattr("src.config.loader.CONFIG_DIR", config_dir)
        monkeypatch.setattr("src.config.loader.CONFIG_PATH", config_path)
        monkeypatch.setattr("src.config.loader.APPS_PATH", apps_path)

        init_default_configs()

        with open(config_path) as f:
            config_content = f.read()

        assert "modes:" in config_content
        assert "defaults:" in config_content
