"""Tests for app registry."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.app.registry import AppRegistry, get_registry


class TestAppRegistry:
    """Test AppRegistry class."""

    def test_registry_creation(self):
        """Test creating a new registry."""
        registry = AppRegistry()
        assert len(registry) == 0

    def test_registry_get(self):
        """Test getting app from registry."""
        registry = AppRegistry()
        registry._apps = {"firefox": {"cmd": ["firefox"]}}
        assert registry.get("firefox") == {"cmd": ["firefox"]}
        assert registry.get("nonexistent") is None

    def test_registry_load(self, monkeypatch):
        """Test load method populates registry."""

        def mock_merge():
            return {"app1": {"cmd": ["app1"]}}

        registry = AppRegistry()
        monkeypatch.setattr(registry, "_merge_app_sources", mock_merge)
        registry.load()
        assert "app1" in registry._apps

    def test_registry_merge_sources(self, tmp_path, monkeypatch):
        """Test _merge_app_sources merges correctly."""
        system_apps = tmp_path / "system.yaml"
        user_apps = tmp_path / "apps.yaml"

        import yaml

        with open(system_apps, "w") as f:
            yaml.dump({"firefox": {"cmd": ["firefox"]}}, f)
        with open(user_apps, "w") as f:
            yaml.dump(
                {"firefox": {"cmd": ["firefox-mod"]}, "vscode": {"cmd": ["code"]}}, f
            )

        monkeypatch.setattr("src.app.registry.SYSTEM_APPS_PATH", system_apps)
        monkeypatch.setattr("src.app.registry.APPS_PATH", user_apps)

        registry = AppRegistry()
        result = registry._merge_app_sources()

        assert result["firefox"]["cmd"] == ["firefox-mod"]
        assert "vscode" in result

    def test_registry_get_or_default(self):
        """Test get_or_default returns default for missing app."""
        registry = AppRegistry()
        registry._apps = {}
        result = registry.get_or_default("missing")
        assert result == {}

    def test_registry_has(self):
        """Test checking if app exists in registry."""
        registry = AppRegistry()
        registry._apps = {"firefox": {}}
        assert registry.has("firefox") is True
        assert registry.has("missing") is False

    def test_registry_keys(self):
        """Test getting all app keys."""
        registry = AppRegistry()
        registry._apps = {"a": {}, "b": {}}
        keys = registry.keys()
        assert "a" in keys
        assert "b" in keys

    def test_registry_items(self):
        """Test getting all app items."""
        registry = AppRegistry()
        registry._apps = {"firefox": {"cmd": ["firefox"]}}
        items = registry.items()
        assert len(items) == 1
        assert items[0][0] == "firefox"

    def test_registry_contains(self):
        """Test 'in' operator support."""
        registry = AppRegistry()
        registry._apps = {"firefox": {}}
        assert "firefox" in registry
        assert "missing" not in registry

    def test_registry_indexing(self):
        """Test dict-style indexing."""
        registry = AppRegistry()
        registry._apps = {"firefox": {"cmd": ["firefox"]}}
        assert registry["firefox"] == {"cmd": ["firefox"]}

    def test_registry_len(self):
        """Test registry length."""
        registry = AppRegistry()
        registry._apps = {"a": {}, "b": {}, "c": {}}
        assert len(registry) == 3

    def test_registry_iteration(self):
        """Test iterating over registry."""
        registry = AppRegistry()
        registry._apps = {"a": {}, "b": {}}
        keys = list(registry)
        assert "a" in keys
        assert "b" in keys


class TestGetRegistry:
    """Test get_registry function."""

    @patch("src.app.registry.AppRegistry")
    def test_get_registry_singleton(self, mock_registry_class):
        """Test get_registry returns singleton instance."""
        mock_registry = MagicMock()
        mock_registry_class.return_value = mock_registry

        from src.app import registry as registry_module

        registry_module._default_registry = None

        result = registry_module.get_registry()
        assert result == mock_registry

        result2 = registry_module.get_registry()
        assert result == result2
