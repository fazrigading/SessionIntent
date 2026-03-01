"""Tests for session state management."""

import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from src.session.state import (
    save_state,
    load_state,
    clear_state,
    get_current_state,
    state_exists,
)


class TestSaveState:
    """Test save_state function."""

    def test_save_state_dev_mode(self, capsys):
        """Test save_state in dev mode."""
        save_state("work", dev_mode=True)
        captured = capsys.readouterr()
        assert "[DEV] Would write state: work" in captured.out

    def test_save_state_creates_file(self, tmp_path, monkeypatch):
        """Test save_state creates state file."""
        state_file = tmp_path / "state" / "current"
        state_file.parent.mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr("src.session.state.STATE_FILE", state_file)
        monkeypatch.setattr("src.session.state.STATE_DIR", tmp_path / "state")

        save_state("work", dev_mode=False)

        assert state_file.exists()
        assert state_file.read_text() == "work"


class TestLoadState:
    """Test load_state function."""

    def test_load_state_no_file(self, tmp_path, monkeypatch):
        """Test load_state when no state file exists."""
        state_file = tmp_path / "state" / "current"
        monkeypatch.setattr("src.session.state.STATE_FILE", state_file)

        result = load_state()
        assert result is None

    def test_load_state_existing_file(self, tmp_path, monkeypatch):
        """Test load_state reads existing file."""
        state_file = tmp_path / "state" / "current"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text("work")

        monkeypatch.setattr("src.session.state.STATE_FILE", state_file)

        result = load_state()
        assert result == "work"

    def test_load_state_strips_whitespace(self, tmp_path, monkeypatch):
        """Test load_state strips whitespace."""
        state_file = tmp_path / "state" / "current"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text("  work  \n")

        monkeypatch.setattr("src.session.state.STATE_FILE", state_file)

        result = load_state()
        assert result == "work"

    def test_load_state_io_error(self, tmp_path, monkeypatch):
        """Test load_state returns None on IOError."""
        state_file = tmp_path / "state" / "current"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text("work")

        monkeypatch.setattr("src.session.state.STATE_FILE", state_file)

        with patch("builtins.open", side_effect=IOError("Permission denied")):
            result = load_state()
            assert result is None


class TestClearState:
    """Test clear_state function."""

    def test_clear_state_dev_mode(self, capsys):
        """Test clear_state in dev mode."""
        clear_state(dev_mode=True)
        captured = capsys.readouterr()
        assert "[DEV] Would clear state" in captured.out

    def test_clear_state_removes_file(self, tmp_path, monkeypatch):
        """Test clear_state removes state file."""
        state_file = tmp_path / "state" / "current"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text("work")

        monkeypatch.setattr("src.session.state.STATE_FILE", state_file)

        clear_state(dev_mode=False)

        assert not state_file.exists()

    def test_clear_state_no_file(self, tmp_path, monkeypatch):
        """Test clear_state when no file exists."""
        state_file = tmp_path / "state" / "current"

        monkeypatch.setattr("src.session.state.STATE_FILE", state_file)

        clear_state(dev_mode=False)

        assert not state_file.exists()

    def test_clear_state_io_error(self, tmp_path, monkeypatch):
        """Test clear_state handles IOError gracefully."""
        state_file = tmp_path / "state" / "current"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text("work")

        monkeypatch.setattr("src.session.state.STATE_FILE", state_file)

        with patch("pathlib.Path.unlink", side_effect=IOError("Permission denied")):
            clear_state(dev_mode=False)

        assert state_file.exists()


class TestGetCurrentState:
    """Test get_current_state function."""

    def test_get_current_state(self, tmp_path, monkeypatch):
        """Test get_current_state is alias for load_state."""
        state_file = tmp_path / "state" / "current"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text("work")

        monkeypatch.setattr("src.session.state.STATE_FILE", state_file)

        result = get_current_state()
        assert result == "work"


class TestStateExists:
    """Test state_exists function."""

    def test_state_exists_true(self, tmp_path, monkeypatch):
        """Test state_exists returns True when file exists."""
        state_file = tmp_path / "state" / "current"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text("work")

        monkeypatch.setattr("src.session.state.STATE_FILE", state_file)

        assert state_exists() is True

    def test_state_exists_false(self, tmp_path, monkeypatch):
        """Test state_exists returns False when file doesn't exist."""
        state_file = tmp_path / "state" / "current"

        monkeypatch.setattr("src.session.state.STATE_FILE", state_file)

        assert state_exists() is False
