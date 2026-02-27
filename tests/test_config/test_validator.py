"""Tests for config validator."""

import pytest
from pathlib import Path

from src.config.validator import (
    validate_config,
    validate_apps,
    validate_config_file,
    validate_apps_file,
    raise_if_invalid,
)


class TestValidateConfig:
    """Test configuration validation."""

    def test_valid_config_with_modes(self):
        """Test valid config with modes only."""
        config = {
            "modes": {
                "work": {"label": "Work"},
            }
        }
        errors = validate_config(config)
        assert errors == []

    def test_valid_config_with_all_fields(self):
        """Test valid config with all fields."""
        config = {
            "version": 1,
            "defaults": {
                "ask_before_kill": True,
                "reuse_workspaces": True,
            },
            "hardware_profiles": {
                "battery": {"disable_modes": ["gaming"]},
                "plugged": {"allow_all": True},
            },
            "modes": {
                "work": {"label": "Work"},
            },
        }
        errors = validate_config(config)
        assert errors == []

    def test_valid_config_minimal(self):
        """Test valid minimal config."""
        config = {"modes": {"test": {"label": "Test", "workspaces": {}}}}
        errors = validate_config(config)
        assert errors == []

    def test_invalid_empty_config(self):
        """Test invalid: empty config dict."""
        config = {}
        errors = validate_config(config)
        assert len(errors) > 0

    def test_invalid_none_config(self):
        """Test invalid: None config."""
        config = None
        errors = validate_config(config)
        assert len(errors) > 0
        assert "Configuration is empty" in errors

    def test_invalid_missing_modes(self):
        """Test invalid: missing modes key."""
        config = {
            "version": 1,
            "defaults": {},
        }
        errors = validate_config(config)
        assert any("Missing required key: 'modes'" in err for err in errors)

    def test_invalid_modes_not_dict(self):
        """Test invalid: modes is not a dict."""
        config = {"modes": "not a dict"}
        errors = validate_config(config)
        assert any("'modes' must be a dictionary" in err for err in errors)

    def test_invalid_defaults_not_dict(self):
        """Test invalid: defaults is not a dict."""
        config = {
            "modes": {"work": {}},
            "defaults": "not a dict",
        }
        errors = validate_config(config)
        assert any("'defaults' must be a dictionary" in err for err in errors)

    def test_invalid_hardware_profiles_not_dict(self):
        """Test invalid: hardware_profiles is not a dict."""
        config = {
            "modes": {"work": {}},
            "hardware_profiles": "not a dict",
        }
        errors = validate_config(config)
        assert any("'hardware_profiles' must be a dictionary" in err for err in errors)

    def test_invalid_empty_modes(self):
        """Test invalid: empty modes dict."""
        config = {"modes": {}}
        errors = validate_config(config)
        assert any("must contain at least one mode" in err for err in errors)


class TestValidateApps:
    """Test apps validation."""

    def test_valid_apps_single(self):
        """Test valid apps with single app."""
        apps = {
            "firefox": {
                "cmd": ["firefox"],
            }
        }
        errors = validate_apps(apps)
        assert errors == []

    def test_valid_apps_multiple(self):
        """Test valid apps with multiple apps."""
        apps = {
            "firefox": {
                "cmd": ["firefox"],
                "check": "firefox",
                "internal_reuse": True,
            },
            "vscode": {
                "cmd": ["code"],
                "flags": {"verbose": "-v"},
            },
        }
        errors = validate_apps(apps)
        assert errors == []

    def test_valid_apps_with_all_fields(self):
        """Test valid apps with all possible fields."""
        apps = {
            "app": {
                "cmd": ["app"],
                "check": "app",
                "internal_reuse": True,
                "flags": {"flag": "--flag"},
                "append_param": "urls",
                "primary_param": "workspace",
            }
        }
        errors = validate_apps(apps)
        assert errors == []

    def test_invalid_empty_apps(self):
        """Test invalid: empty apps dict."""
        apps = {}
        errors = validate_apps(apps)
        assert len(errors) > 0
        assert any("Application registry is empty" in err for err in errors)

    def test_invalid_not_dict(self):
        """Test invalid: apps is not a dict."""
        apps = "not a dict"
        errors = validate_apps(apps)
        assert len(errors) > 0
        assert "Applications must be a dictionary" in errors

    def test_invalid_app_definition_not_dict(self):
        """Test invalid: app definition is not a dict."""
        apps = {"app": "not a dict"}
        errors = validate_apps(apps)
        assert any("definition must be a dictionary" in err for err in errors)

    def test_invalid_cmd_not_list(self):
        """Test invalid: cmd is not a list."""
        apps = {
            "app": {
                "cmd": "not a list",
            }
        }
        errors = validate_apps(apps)
        assert any("'cmd' must be a list or tuple" in err for err in errors)

    def test_invalid_cmd_as_tuple(self):
        """Test valid: cmd as tuple is accepted."""
        apps = {
            "app": {
                "cmd": ("app",),
            }
        }
        errors = validate_apps(apps)
        assert errors == []

    def test_invalid_flags_not_dict(self):
        """Test invalid: flags is not a dict."""
        apps = {
            "app": {
                "cmd": ["app"],
                "flags": "not a dict",
            }
        }
        errors = validate_apps(apps)
        assert any("'flags' must be a dictionary" in err for err in errors)

    def test_invalid_multiple_errors(self):
        """Test invalid: multiple validation errors."""
        apps = {
            "app1": "not dict",
            "app2": {"cmd": "not list"},
            "app3": {"cmd": ["cmd"], "flags": "not dict"},
        }
        errors = validate_apps(apps)
        assert len(errors) >= 3


class TestValidateConfigFile:
    """Test config file validation."""

    def test_validate_nonexistent_file(self):
        """Test validating nonexistent file."""
        file_path = Path("/nonexistent/config.yaml")
        errors = validate_config_file(file_path)
        assert len(errors) == 1
        assert "File not found" in errors[0]

    def test_validate_invalid_yaml_file(self, tmp_path):
        """Test validating invalid YAML file."""
        file_path = tmp_path / "config.yaml"
        file_path.write_text("invalid: yaml: : content")

        errors = validate_config_file(file_path)
        assert len(errors) == 1
        assert "Invalid YAML" in errors[0]

    def test_validate_valid_config_file(self, tmp_path):
        """Test validating valid config file."""
        file_path = tmp_path / "config.yaml"
        file_path.write_text("modes:\n  work:\n    label: Work\n")

        errors = validate_config_file(file_path)
        assert errors == []


class TestValidateAppsFile:
    """Test apps file validation."""

    def test_validate_nonexistent_file(self):
        """Test validating nonexistent file."""
        file_path = Path("/nonexistent/apps.yaml")
        errors = validate_apps_file(file_path)
        assert len(errors) == 1
        assert "File not found" in errors[0]

    def test_validate_invalid_yaml_file(self, tmp_path):
        """Test validating invalid YAML file."""
        file_path = tmp_path / "apps.yaml"
        file_path.write_text("invalid: yaml: : content")

        errors = validate_apps_file(file_path)
        assert len(errors) == 1
        assert "Invalid YAML" in errors[0]

    def test_validate_valid_apps_file(self, tmp_path):
        """Test validating valid apps file."""
        file_path = tmp_path / "apps.yaml"
        file_path.write_text("firefox:\n  cmd:\n    - firefox\n")

        errors = validate_apps_file(file_path)
        assert errors == []


class TestRaiseIfInvalid:
    """Test raise_if_invalid function."""

    def test_raise_if_invalid_no_errors(self):
        """Test that no exception is raised with no errors."""
        errors = []
        raise_if_invalid(errors)

    def test_raise_if_invalid_with_errors(self):
        """Test that ValueError is raised with errors."""
        errors = ["Error 1", "Error 2"]
        with pytest.raises(ValueError) as exc_info:
            raise_if_invalid(errors)
        assert "Error 1" in str(exc_info.value)
        assert "Error 2" in str(exc_info.value)

    def test_raise_if_invalid_with_context(self):
        """Test that context is included in error message."""
        errors = ["Some error"]
        with pytest.raises(ValueError) as exc_info:
            raise_if_invalid(errors, context=" (in modes)")
        assert "Validation failed (in modes)" in str(exc_info.value)
