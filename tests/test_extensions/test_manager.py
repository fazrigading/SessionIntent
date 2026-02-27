"""Tests for extensions package."""

import pytest
from unittest.mock import patch, MagicMock

from src.extensions.manager import (
    resolve_extension_id,
    list_extensions,
    get_enabled_extensions,
    enable_extension,
    disable_extension,
    apply_extensions,
    EXTENSION_REGISTRY,
)


class TestResolveExtensionId:
    """Test extension ID resolution."""

    def test_resolve_by_uuid(self):
        """Test resolving by UUID directly."""
        uuid = "dash-to-panel@jderose9.github.com"
        assert resolve_extension_id(uuid) == uuid

    def test_resolve_by_name(self):
        """Test resolving by name."""
        assert (
            resolve_extension_id("Dash to Panel") == "dash-to-panel@jderose9.github.com"
        )
        assert (
            resolve_extension_id("dash to panel") == "dash-to-panel@jderose9.github.com"
        )

    def test_resolve_by_hyphenated_name(self):
        """Test resolving by hyphenated name."""
        assert (
            resolve_extension_id("dash-to-panel") == "dash-to-panel@jderose9.github.com"
        )
        assert (
            resolve_extension_id("workspace-indicator")
            == "workspace-indicator@gnome-shell-extensions.gcampax.github.com"
        )

    def test_resolve_unknown(self):
        """Test resolving unknown extension."""
        assert resolve_extension_id("Unknown Extension XYZ123") is None


class TestListExtensions:
    """Test listing extensions."""

    def test_list_extensions_dev_mode(self):
        """Test listing extensions in dev mode."""
        result = list_extensions(dev_mode=True)
        assert result == []

    @patch("subprocess.run")
    def test_list_extensions_real(self, mock_run):
        """Test listing extensions with mock."""
        mock_run.return_value = MagicMock(
            returncode=0, stdout="ext1@example.com\next2@example.com\n"
        )
        result = list_extensions(dev_mode=False)
        assert result == ["ext1@example.com", "ext2@example.com"]


class TestApplyExtensions:
    """Test applying extensions."""

    def test_apply_extensions_dev_mode(self):
        """Test applying extensions in dev mode."""
        config = {"enable": ["dash-to-panel"], "disable": ["caffeine"]}
        messages = apply_extensions(config, dev_mode=True)

        assert any("dash-to-panel@jderose9.github.com" in msg for msg in messages)
        assert any("caffeine@patapon.info" in msg for msg in messages)

    def test_apply_extensions_enable_only(self):
        """Test applying extensions with only enable list."""
        config = {"enable": ["dash-to-panel"]}
        messages = apply_extensions(config, dev_mode=True)

        assert len(messages) == 1
        assert "enable" in messages[0].lower()

    def test_apply_extensions_disable_only(self):
        """Test applying extensions with only disable list."""
        config = {"disable": ["caffeine"]}
        messages = apply_extensions(config, dev_mode=True)

        assert len(messages) == 1
        assert "disable" in messages[0].lower()

    def test_apply_extensions_empty(self):
        """Test applying empty extensions config."""
        messages = apply_extensions({}, dev_mode=True)
        assert messages == []


class TestExtensionRegistry:
    """Test extension registry."""

    def test_registry_not_empty(self):
        """Test that registry contains extensions."""
        assert len(EXTENSION_REGISTRY) > 0

    def test_registry_has_dash_to_panel(self):
        """Test that dash-to-panel is in registry."""
        assert "dash to panel" in EXTENSION_REGISTRY

    def test_registry_values_are_uuids(self):
        """Test that all registry values are valid UUIDs."""
        for name, uuid in EXTENSION_REGISTRY.items():
            assert "@" in uuid, f"Invalid UUID for {name}: {uuid}"
