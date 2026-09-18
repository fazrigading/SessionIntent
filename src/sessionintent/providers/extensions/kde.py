"""
SessionIntent KDE Extension Provider
Plasma applet listing via kpackagetool (6, then 5).
Programmatic enable/disable is not reliably scriptable, so those
operations report a manual step instead of pretending to work.
"""

from __future__ import annotations

import shutil
import subprocess
from typing import Any, List


def _kpackagetool() -> str | None:
    """Preferred kpackagetool binary, or None if missing."""
    for tool in ("kpackagetool6", "kpackagetool5"):
        if shutil.which(tool):
            return tool
    return None


def _run(args: list[str], dev_mode: bool = False) -> str | None:
    """Run kpackagetool and return stripped stdout, or None on failure."""
    if dev_mode:
        return None
    try:
        result = subprocess.run(
            args, capture_output=True, text=True, timeout=10, check=True
        )
        return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return None


class KdeExtensionProvider:
    """KDE Plasma applet provider via kpackagetool."""

    def __init__(self, dev_mode: bool = False) -> None:
        self._dev_mode = dev_mode

    def list(self) -> List[str]:
        if self._dev_mode:
            return ["org.kde.plasma.systemmonitor"]
        tool = _kpackagetool()
        if tool is None:
            return []
        out = _run([tool, "--list", "-t", "Plasma/Applet"])
        if not out:
            return []
        return [line.strip() for line in out.split("\n") if line.strip()]

    def get_info(self, ext_id: str) -> dict[str, Any] | None:
        if self._dev_mode:
            return {"id": ext_id, "source": "mock"}
        if ext_id in self.list():
            return {"id": ext_id}
        return None

    def _manual(self, action: str, ext_id: str) -> tuple[bool, str]:
        return (
            False,
            f"Plasma applets cannot be {action}d programmatically "
            f"({ext_id}); add/remove it manually in desktop settings",
        )

    def enable(self, ext_id: str) -> tuple[bool, str]:
        if self._dev_mode:
            return True, f"[DEV] Would enable applet: {ext_id}"
        return self._manual("enable", ext_id)

    def disable(self, ext_id: str) -> tuple[bool, str]:
        if self._dev_mode:
            return True, f"[DEV] Would disable applet: {ext_id}"
        return self._manual("disable", ext_id)

    def apply(self, config: dict[str, List[str]]) -> List[str]:
        messages: list[str] = []
        for ext_id in config.get("enable", []):
            _, msg = self.enable(ext_id)
            messages.append(msg)
        for ext_id in config.get("disable", []):
            _, msg = self.disable(ext_id)
            messages.append(msg)
        return messages

    def ensure(self) -> tuple[bool, str]:
        if self._dev_mode:
            return True, "[DEV] Would ensure Plasma tooling"
        if _kpackagetool() is None:
            return False, "kpackagetool not found; install plasma SDK tools"
        return True, "Plasma tooling available"


__all__ = ["KdeExtensionProvider"]
