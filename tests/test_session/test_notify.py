"""Tests for desktop notifications."""

from unittest.mock import MagicMock, patch

from sessionintent.session.notify import (
    notify_error,
    notify_mode_change,
    send_notification,
)


class TestSendNotificationDev:
    def test_dev_mode_prints(self, capsys):
        assert send_notification("T", "M", dev_mode=True) is True
        assert "[DEV] Notification: T - M" in capsys.readouterr().out


class TestSendNotificationReal:
    @patch("subprocess.run")
    def test_notify_send(self, mock_run):
        mock_run.return_value = MagicMock()
        assert send_notification("T", "M") is True
        assert mock_run.call_args[0][0][0] == "notify-send"

    @patch("sessionintent.session.notify.HAS_PYNOTIFY", False)
    @patch("subprocess.run")
    def test_all_tools_missing_returns_false(self, mock_run):
        mock_run.side_effect = FileNotFoundError
        assert send_notification("T", "M") is False

    def test_mode_change_helpers(self, capsys):
        assert notify_mode_change("work", "Work", dev_mode=True) is True
        assert notify_error("boom", dev_mode=True) is True
        out = capsys.readouterr().out
        assert "Switched to mode: Work" in out
        assert "boom" in out
