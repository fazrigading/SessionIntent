"""
SessionIntent Session Package
Provides session orchestration and state management.
"""

from .manager import SessionManager
from .state import save_state, load_state, clear_state, get_current_state, state_exists
from .log import debug, info, warning, error, critical, get_log_path, clear_log
from .snapshot import WindowState, save_snapshot, load_snapshot, restore_snapshot
from .notify import send_notification, notify_mode_change, notify_error

__all__ = [
    "SessionManager",
    "save_state",
    "load_state",
    "clear_state",
    "get_current_state",
    "state_exists",
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    "get_log_path",
    "clear_log",
    "WindowState",
    "save_snapshot",
    "load_snapshot",
    "restore_snapshot",
    "send_notification",
    "notify_mode_change",
    "notify_error",
]
