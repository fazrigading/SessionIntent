"""Tests for version: 1 to version: 2 config migration."""

from sessionintent.config.migration import (
    config_version,
    migrate_v1_to_v2,
    migration_notice,
    needs_migration,
)


class TestConfigVersion:
    def test_v2(self):
        assert config_version({"version": 2}) == 2

    def test_v1_explicit(self):
        assert config_version({"version": 1}) == 1

    def test_undeclared_is_v1(self):
        assert config_version({"modes": {}}) == 1
        assert config_version({}) == 1


class TestNeedsMigration:
    def test_v2_clean(self):
        assert needs_migration({"version": 2, "modes": {}}) is False

    def test_v1_needs_migration(self):
        assert needs_migration({"version": 1, "modes": {}}) is True


class TestMigrateV1ToV2:
    def test_sets_version(self):
        migrated, stripped = migrate_v1_to_v2({"modes": {"work": {}}})
        assert migrated["version"] == 2
        assert stripped == []

    def test_strips_retired_keys(self):
        config = {
            "modes": {
                "work": {
                    "schedule": {"time": "08:00"},
                    "settings": {},
                    "hardware": {"battery_only": True},
                    "workspaces": {},
                }
            },
            "settings": {},
        }
        migrated, stripped = migrate_v1_to_v2(config)
        assert migrated["version"] == 2
        assert "settings" in stripped
        assert "modes.work.schedule" in stripped
        assert "modes.work.hardware.battery_only" in stripped
        assert "schedule" not in migrated["modes"]["work"]

    def test_does_not_mutate_input(self):
        config = {"modes": {"work": {"schedule": {}}}}
        migrate_v1_to_v2(config)
        assert "schedule" in config["modes"]["work"]


class TestMigrationNotice:
    def test_points_to_guide(self):
        notice = migration_notice()
        assert "migration" in notice.lower()
        assert "MIGRATION" in notice

    def test_lists_stripped_keys(self):
        notice = migration_notice(["modes.work.schedule"])
        assert "modes.work.schedule" in notice
