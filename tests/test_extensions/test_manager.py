"""Tests for extensions package."""

import pytest
from unittest.mock import patch, MagicMock
from subprocess import CalledProcessError

from src.extensions.manager import (
    resolve_extension_id,
    list_extensions,
    get_enabled_extensions,
    get_extension_info,
    enable_extension,
    disable_extension,
    apply_extensions,
    is_extension_installed,
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


class TestResolveExtensionIdPartialMatch:
    """Test partial matching in extension resolution."""

    def test_resolve_partial_match_identifier_in_name(self):
        """Test partial match where identifier is contained in name."""
        result = resolve_extension_id("dash")
        assert result == "dash-to-panel@jderose9.github.com"

    def test_resolve_partial_match_name_in_identifier(self):
        """Test partial match where name is contained in identifier."""
        result = resolve_extension_id("dash to panel app")
        assert result == "dash-to-panel@jderose9.github.com"

    def test_resolve_with_underscore(self):
        """Test resolving with underscore in name."""
        result = resolve_extension_id("appfolders manager")
        assert result == "appfolders-manager@ddubson.gmail.com"


class TestListExtensionsErrors:
    """Test error handling in list_extensions."""

    @patch("subprocess.run")
    def test_list_extensions_file_not_found(self, mock_run):
        """Test list_extensions when gnome-extensions not found."""
        mock_run.side_effect = FileNotFoundError("gnome-extensions")
        result = list_extensions(dev_mode=False)
        assert result == []

    @patch("subprocess.run")
    def test_list_extensions_called_process_error(self, mock_run):
        """Test list_extensions when command fails."""
        mock_run.side_effect = CalledProcessError(1, "gnome-extensions")
        result = list_extensions(dev_mode=False)
        assert result == []


class TestGetEnabledExtensions:
    """Test get_enabled_extensions function."""

    def test_get_enabled_extensions_dev_mode(self):
        """Test get_enabled_extensions in dev mode."""
        result = get_enabled_extensions(dev_mode=True)
        assert result == ["dash-to-panel@jderose9.github.com"]

    @patch("subprocess.run")
    def test_get_enabled_extensions_real(self, mock_run):
        """Test get_enabled_extensions with mock."""
        mock_run.return_value = MagicMock(
            returncode=0, stdout="ext1@example.com\next2@example.com\n"
        )
        result = get_enabled_extensions(dev_mode=False)
        assert result == ["ext1@example.com", "ext2@example.com"]

    @patch("subprocess.run")
    def test_get_enabled_extensions_file_not_found(self, mock_run):
        """Test get_enabled_extensions when gnome-extensions not found."""
        mock_run.side_effect = FileNotFoundError("gnome-extensions")
        result = get_enabled_extensions(dev_mode=False)
        assert result == []


class TestGetExtensionInfo:
    """Test get_extension_info function."""

    def test_get_extension_info_dev_mode_enabled(self):
        """Test get_extension_info in dev mode for enabled extension."""
        result = get_extension_info("dash-to-panel@jderose9.github.com", dev_mode=True)
        assert result is not None
        assert result["uuid"] == "dash-to-panel@jderose9.github.com"
        assert result["state"] == "ENABLED"

    def test_get_extension_info_dev_mode_disabled(self):
        """Test get_extension_info in dev mode for disabled extension."""
        result = get_extension_info("caffeine@patapon.info", dev_mode=True)
        assert result is not None
        assert result["state"] == "DISABLED"

    @patch("subprocess.run")
    def test_get_extension_info_real(self, mock_run):
        """Test get_extension_info with mock."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="""Name: Dash to Panel
UUID: dash-to-panel@jderose9.github.com
State: Enabled
""",
        )
        result = get_extension_info("dash-to-panel@jderose9.github.com", dev_mode=False)
        assert result is not None
        assert result.get("uuid") == "dash-to-panel@jderose9.github.com"

    @patch("subprocess.run")
    def test_get_extension_info_file_not_found(self, mock_run):
        """Test get_extension_info when gnome-extensions not found."""
        mock_run.side_effect = FileNotFoundError("gnome-extensions")
        result = get_extension_info("dash-to-panel@jderose9.github.com", dev_mode=False)
        assert result is None

    @patch("subprocess.run")
    def test_get_extension_info_called_process_error(self, mock_run):
        """Test get_extension_info when command fails."""
        mock_run.side_effect = CalledProcessError(1, "gnome-extensions")
        result = get_extension_info("dash-to-panel@jderose9.github.com", dev_mode=False)
        assert result is None


class TestEnableExtension:
    """Test enable_extension function."""

    @patch("subprocess.run")
    def test_enable_extension_success(self, mock_run):
        """Test enable_extension success."""
        mock_run.return_value = MagicMock(returncode=0)
        success, msg = enable_extension("test@ext.com", dev_mode=False)
        assert success is True
        assert "Enabled" in msg

    @patch("src.extensions.manager.get_extension_info")
    def test_enable_extension_not_found(self, mock_get_info):
        """Test enable_extension when extension doesn't exist."""
        mock_get_info.return_value = None
        success, msg = enable_extension("nonexistent@ext.com", dev_mode=False)
        assert success is False
        assert "does not exist" in msg

    @patch("src.extensions.manager.get_extension_info")
    @patch("subprocess.run")
    def test_enable_extension_file_not_found(self, mock_run, mock_get_info):
        """Test enable_extension when gnome-extensions not found."""
        mock_get_info.return_value = {"uuid": "test@ext.com"}
        mock_run.side_effect = FileNotFoundError("gnome-extensions")
        success, msg = enable_extension("test@ext.com", dev_mode=False)
        assert success is False
        assert "not found" in msg

    @patch("src.extensions.manager.get_extension_info")
    @patch("subprocess.run")
    def test_enable_extension_called_process_error(self, mock_run, mock_get_info):
        """Test enable_extension when command fails."""
        mock_get_info.return_value = {"uuid": "test@ext.com"}
        mock_run.side_effect = CalledProcessError(1, "gnome-extensions", stderr="error")
        success, msg = enable_extension("test@ext.com", dev_mode=False)
        assert success is False
        assert "Failed to enable" in msg


class TestDisableExtension:
    """Test disable_extension function."""

    @patch("subprocess.run")
    def test_disable_extension_success(self, mock_run):
        """Test disable_extension success."""
        mock_run.return_value = MagicMock(returncode=0)
        success, msg = disable_extension("test@ext.com", dev_mode=False)
        assert success is True
        assert "Disabled" in msg

    @patch("src.extensions.manager.get_extension_info")
    def test_disable_extension_not_found(self, mock_get_info):
        """Test disable_extension when extension doesn't exist."""
        mock_get_info.return_value = None
        success, msg = disable_extension("nonexistent@ext.com", dev_mode=False)
        assert success is False
        assert "does not exist" in msg

    @patch("src.extensions.manager.get_extension_info")
    @patch("subprocess.run")
    def test_disable_extension_file_not_found(self, mock_run, mock_get_info):
        """Test disable_extension when gnome-extensions not found."""
        mock_get_info.return_value = {"uuid": "test@ext.com"}
        mock_run.side_effect = FileNotFoundError("gnome-extensions")
        success, msg = disable_extension("test@ext.com", dev_mode=False)
        assert success is False
        assert "not found" in msg

    @patch("src.extensions.manager.get_extension_info")
    @patch("subprocess.run")
    def test_disable_extension_called_process_error(self, mock_run, mock_get_info):
        """Test disable_extension when command fails."""
        mock_get_info.return_value = {"uuid": "test@ext.com"}
        mock_run.side_effect = CalledProcessError(1, "gnome-extensions", stderr="error")
        success, msg = disable_extension("test@ext.com", dev_mode=False)
        assert success is False
        assert "Failed to disable" in msg


class TestApplyExtensionsErrors:
    """Test error handling in apply_extensions."""

    def test_apply_extensions_unknown_enable(self):
        """Test apply_extensions with unknown extension to enable."""
        config = {"enable": ["unknown-extension-xyz"]}
        messages = apply_extensions(config, dev_mode=True)
        assert any("not recognized" in msg for msg in messages)

    def test_apply_extensions_unknown_disable(self):
        """Test apply_extensions with unknown extension to disable."""
        config = {"disable": ["unknown-extension-xyz"]}
        messages = apply_extensions(config, dev_mode=True)
        assert any("not recognized" in msg for msg in messages)


class TestIsExtensionInstalled:
    """Test is_extension_installed function."""

    def test_is_extension_installed_dev_mode(self):
        """Test is_extension_installed in dev mode."""
        result = is_extension_installed("test@ext.com", dev_mode=True)
        assert result is True

    @patch("subprocess.run")
    def test_is_extension_installed_found(self, mock_run):
        """Test is_extension_installed when extension is installed."""
        mock_run.return_value = MagicMock(
            returncode=0, stdout="ext1@example.com\next2@example.com\n"
        )
        result = is_extension_installed("ext2@example.com", dev_mode=False)
        assert result is True

    @patch("subprocess.run")
    def test_is_extension_installed_not_found(self, mock_run):
        """Test is_extension_installed when extension is not installed."""
        mock_run.return_value = MagicMock(
            returncode=0, stdout="ext1@example.com\next2@example.com\n"
        )
        result = is_extension_installed("nonexistent@ext.com", dev_mode=False)
        assert result is False
