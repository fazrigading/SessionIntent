"""Tests for hardware power detection."""

from unittest.mock import patch

from src.hardware.power import is_on_ac


class TestIsOnAC:
    """Test AC power detection."""

    def test_on_ac_power(self, tmp_path):
        """Test detection when system is on AC power."""
        ac_file = tmp_path / "AC"
        ac_online = ac_file / "online"
        ac_online.parent.mkdir(parents=True, exist_ok=True)

        with open(ac_online, "w") as f:
            f.write("1\n")

        with patch("src.hardware.power._AC_PATH", str(ac_online)):
            result = is_on_ac()
            assert result is True

    def test_on_battery_power(self, tmp_path):
        """Test detection when system is on battery power."""
        ac_file = tmp_path / "AC"
        ac_online = ac_file / "online"
        ac_online.parent.mkdir(parents=True, exist_ok=True)

        with open(ac_online, "w") as f:
            f.write("0\n")

        with patch("src.hardware.power._AC_PATH", str(ac_online)):
            result = is_on_ac()
            assert result is False

    def test_ac_file_missing(self):
        """Test defaults to True when AC file doesn't exist."""
        with patch("src.hardware.power._AC_PATH", "/nonexistent/path"):
            result = is_on_ac()
            assert result is True

    def test_ac_file_read_error(self, tmp_path):
        """Test defaults to True when AC file cannot be read."""
        ac_file = tmp_path / "AC"
        ac_online = ac_file / "online"
        ac_online.parent.mkdir(parents=True, exist_ok=True)

        with open(ac_online, "w") as f:
            f.write("1\n")

        with patch("src.hardware.power._AC_PATH", str(ac_online)):
            with patch("builtins.open", side_effect=IOError("Permission denied")):
                result = is_on_ac()
                assert result is True
