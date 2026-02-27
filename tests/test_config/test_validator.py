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

    @pytest.mark.parametrize(
        "config,valid",
        [
            ({"modes": {"work": {"label": "Work"}}}, True),
            (
                {
                    "version": 1,
                    "defaults": {"ask_before_kill": True},
                    "modes": {"work": {}},
                },
                True,
            ),
            ({}, False),
            ({"version": 1}, False),
            ({"modes": {}}, False),
        ],
    )
    def test_validate_config(self, config, valid):
        """Test config validation with various inputs."""
        errors = validate_config(config)
        if valid:
            assert errors == [], f"Expected valid but got errors: {errors}"
        else:
            assert len(errors) > 0

    @pytest.mark.parametrize(
        "config",
        [
            {"modes": "not a dict"},
            {"modes": {"work": {}}, "defaults": "not a dict"},
            {"modes": {"work": {}}, "hardware_profiles": "not a dict"},
        ],
    )
    def test_validate_config_wrong_types(self, config):
        """Test config validation with wrong types."""
        errors = validate_config(config)
        assert len(errors) > 0


class TestValidateApps:
    """Test apps validation."""

    @pytest.mark.parametrize(
        "apps,valid",
        [
            ({"firefox": {"cmd": ["firefox"]}}, True),
            ({"app1": {"cmd": ["a"]}, "app2": {"cmd": ["b"]}}, True),
            ({}, False),
        ],
    )
    def test_validate_apps(self, apps, valid):
        """Test apps validation with various inputs."""
        errors = validate_apps(apps)
        if valid:
            assert errors == [], f"Expected valid but got errors: {errors}"
        else:
            assert len(errors) > 0

    @pytest.mark.parametrize(
        "apps",
        [
            "not a dict",
            {"app": "not a dict"},
            {"app": {"cmd": "not a list"}},
            {"app": {"cmd": ["cmd"], "flags": "not a dict"}},
        ],
    )
    def test_validate_apps_invalid(self, apps):
        """Test apps validation with invalid inputs."""
        errors = validate_apps(apps)
        assert len(errors) > 0


class TestValidateConfigFile:
    """Test config file validation."""

    def test_validate_nonexistent_file(self):
        """Test validating nonexistent file."""
        errors = validate_config_file(Path("/nonexistent/config.yaml"))
        assert len(errors) == 1
        assert "File not found" in errors[0]

    def test_validate_invalid_yaml_file(self, tmp_path):
        """Test validating invalid YAML file."""
        file_path = tmp_path / "config.yaml"
        file_path.write_text("invalid: yaml: : content")
        errors = validate_config_file(file_path)
        assert len(errors) == 1
        assert "Invalid YAML" in errors[0]


class TestValidateAppsFile:
    """Test apps file validation."""

    def test_validate_nonexistent_file(self):
        """Test validating nonexistent file."""
        errors = validate_apps_file(Path("/nonexistent/apps.yaml"))
        assert len(errors) == 1
        assert "File not found" in errors[0]


class TestRaiseIfInvalid:
    """Test raise_if_invalid function."""

    def test_raise_if_invalid_no_errors(self):
        """Test that no exception is raised with no errors."""
        raise_if_invalid([])

    def test_raise_if_invalid_with_errors(self):
        """Test that ValueError is raised with errors."""
        with pytest.raises(ValueError) as exc_info:
            raise_if_invalid(["Error 1", "Error 2"])
        assert "Error 1" in str(exc_info.value)
