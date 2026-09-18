"""Tests for the plugin system and its SessionManager wiring."""

from unittest.mock import patch

from sessionintent.plugins.system import Plugin, PluginManager


class FailingPlugin(Plugin):
    name = "failing"

    def on_mode_apply(self, mode_name, config):
        raise RuntimeError("boom")

    def on_mode_applied(self, mode_name):
        raise RuntimeError("boom")


class PrefixPlugin(Plugin):
    name = "prefix"

    def on_mode_apply(self, mode_name, config):
        config = dict(config)
        config["label"] = "hooked"
        return config


class TestPluginManager:
    def test_load_and_hooks(self):
        manager = PluginManager()
        assert manager.load_plugin(PrefixPlugin()) is True
        assert manager.trigger_hook("on_mode_apply", "work", {}) == []
        assert manager.get_plugin("prefix") is not None

    def test_refused_plugin(self):
        class Refusing(Plugin):
            name = "refusing"

            def on_load(self):
                return False

        assert PluginManager().load_plugin(Refusing()) is False

    def test_unload(self):
        manager = PluginManager()
        manager.load_plugin(PrefixPlugin())
        assert manager.unload_plugin("prefix") is True
        assert manager.unload_plugin("prefix") is False

    def test_discover_skips_private_and_missing_dir(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "sessionintent.plugins.system.PLUGIN_DIR", tmp_path / "plugins"
        )
        PluginManager().discover_plugins()  # Creates the dir, loads nothing.
        assert (tmp_path / "plugins").exists()

    def test_discover_tolerates_broken_plugin(self, tmp_path, monkeypatch):
        plugin_dir = tmp_path / "plugins"
        plugin_dir.mkdir()
        (plugin_dir / "broken.py").write_text("raise RuntimeError('bad plugin')\n")
        (plugin_dir / "_private.py").write_text("X = 1\n")
        monkeypatch.setattr("sessionintent.plugins.system.PLUGIN_DIR", plugin_dir)
        manager = PluginManager()
        manager.discover_plugins()  # Must not raise.
        assert manager.get_plugins() == {}


class TestManagerWiring:
    def test_apply_runs_plugin_and_notify(self, tmp_path, monkeypatch):
        from sessionintent.session.manager import SessionManager

        state_file = tmp_path / "state" / "current"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr("sessionintent.session.state.STATE_FILE", state_file)

        config_path = tmp_path / "config.yaml"
        config_path.write_text("version: 2\nmodes:\n  work:\n    workspaces: {}\n")

        manager = PluginManager()
        manager.load_plugin(PrefixPlugin())
        manager.load_plugin(FailingPlugin())

        with patch("sessionintent.constants.paths.CONFIG_PATH", config_path):
            with patch(
                "sessionintent.session.manager.get_plugin_manager",
                return_value=manager,
            ):
                with patch(
                    "sessionintent.session.manager.notify_mode_change"
                ) as mock_notify:
                    mgr = SessionManager(
                        config_path=str(config_path), dev_mode=False
                    )
                    mgr.apply_mode("work")

        mock_notify.assert_called_once_with("work", "hooked", False)
        assert state_file.exists()

    def test_dev_mode_skips_plugins(self, tmp_path, capsys):
        from sessionintent.session.manager import SessionManager

        config_path = tmp_path / "config.yaml"
        config_path.write_text("version: 2\nmodes:\n  work:\n    workspaces: {}\n")

        with patch("sessionintent.constants.paths.CONFIG_PATH", config_path):
            mgr = SessionManager(config_path=str(config_path), dev_mode=True)
            mgr.apply_mode("work")

        assert "[DEV] Notification" in capsys.readouterr().out
