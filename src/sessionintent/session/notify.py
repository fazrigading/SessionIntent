"""
SessionIntent Desktop Notifications
Provides desktop notification support.
"""

from __future__ import annotations

import subprocess
from ..session.log import error

try:
    import pynotify  # type: ignore[import-not-found]

    HAS_PYNOTIFY = True
except ImportError:
    HAS_PYNOTIFY = False


NOTIFICATION_ICON = "dialog-information"


class Notification:
    """Desktop notification."""

    def __init__(
        self,
        title: str,
        message: str,
        icon: str = NOTIFICATION_ICON,
        urgency: str = "normal",
    ) -> None:
        self.title = title
        self.message = message
        self.icon = icon
        self.urgency = urgency


def send_notification(
    title: str,
    message: str,
    icon: str = NOTIFICATION_ICON,
    urgency: str = "normal",
    dev_mode: bool = False,
) -> bool:
    """
    Send a desktop notification.

    Args:
        title: Notification title
        message: Notification message
        icon: Icon name
        urgency: Urgency level (low, normal, critical)
        dev_mode: If True, print instead of sending

    Returns:
        True if successful
    """
    if dev_mode:
        print(f"[DEV] Notification: {title} - {message}")
        return True

    if HAS_PYNOTIFY:
        try:
            pynotify.init("SessionIntent")
            n = pynotify.Notification(title, message, icon)
            n.set_urgency(urgency)
            n.show()
            return True
        except Exception:
            pass

    try:
        subprocess.run(
            [
                "notify-send",
                "-i",
                icon,
                "-u",
                urgency,
                title,
                message,
            ],
            capture_output=True,
            check=True,
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        try:
            subprocess.run(
                [
                    "dbus-send",
                    "--session",
                    "--dest=org.freedesktop.Notifications",
                    "--type=method_call",
                    "--print-reply",
                    "/org/freedesktop/Notifications",
                    "org.freedesktop.Notifications.Notify",
                    "string:SessionIntent",
                    "uint32:0",
                    "string:" + icon,
                    "string:" + title,
                    "string:" + message,
                    "array:string:",
                    "dict:string:variant:",
                ],
                capture_output=True,
            )
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

    error("Failed to send desktop notification")
    return False


def notify_mode_change(
    mode_name: str,
    mode_label: str,
    dev_mode: bool = False,
) -> bool:
    """Notify that mode has changed."""
    return send_notification(
        title="SessionIntent",
        message=f"Switched to mode: {mode_label}",
        icon="preferences-system",
        dev_mode=dev_mode,
    )


def notify_error(
    message: str,
    dev_mode: bool = False,
) -> bool:
    """Notify of an error."""
    return send_notification(
        title="SessionIntent Error",
        message=message,
        icon="dialog-error",
        urgency="critical",
        dev_mode=dev_mode,
    )


def notify_scheduled_switch(
    mode_name: str,
    mode_label: str,
    dev_mode: bool = False,
) -> bool:
    """Notify of scheduled mode switch."""
    return send_notification(
        title="SessionIntent",
        message=f"Auto-switching to: {mode_label}",
        icon="calendar",
        dev_mode=dev_mode,
    )


__all__ = [
    "Notification",
    "send_notification",
    "notify_mode_change",
    "notify_error",
    "notify_scheduled_switch",
]