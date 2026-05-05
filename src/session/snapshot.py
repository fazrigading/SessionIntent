"""
SessionIntent Session Snapshots
Manages saving and restoring window positions using GNOME's window manager.
"""

from __future__ import annotations

import subprocess
from typing import Any

from ..constants import STATE_DIR
from .log import info, warning, error


SNAPSHOT_DIR = STATE_DIR / "snapshots"


class WindowState:
    """Represents a window's state."""

    def __init__(
        self,
        app_id: str,
        window_title: str,
        x: int,
        y: int,
        width: int,
        height: int,
        workspace: int,
    ) -> None:
        self.app_id = app_id
        self.window_title = window_title
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.workspace = workspace

    def to_dict(self) -> dict[str, Any]:
        return {
            "app_id": self.app_id,
            "window_title": self.window_title,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "workspace": self.workspace,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WindowState:
        return cls(
            app_id=data["app_id"],
            window_title=data["window_title"],
            x=data["x"],
            y=data["y"],
            width=data["width"],
            height=data["height"],
            workspace=data["workspace"],
        )


def _get_window_list() -> list[WindowState]:
    """Get list of windows using available tools."""
    windows: list[WindowState] = []

    try:
        result = subprocess.run(
            ["wmctl", "jd", "-l"],
            capture_output=True,
            text=True,
            check=True,
        )
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split(":", 6)
            if len(parts) >= 7:
                windows.append(
                    WindowState(
                        app_id=parts[0],
                        window_title=parts[1],
                        x=int(parts[2]),
                        y=int(parts[3]),
                        width=int(parts[4]),
                        height=int(parts[5]),
                        workspace=int(parts[6]),
                    )
                )
    except (subprocess.SubprocessError, FileNotFoundError, ValueError):
        try:
            result = subprocess.run(
                ["xdotool", "search", "--onlyvisible", "--name", ".*"],
                capture_output=True,
                text=True,
            )
            for wid in result.stdout.strip().split("\n"):
                if not wid:
                    continue
                try:
                    win_info = subprocess.run(
                        [
                            "xdotool",
                            "getwindowgeometry",
                            "--shell",
                            wid,
                        ],
                        capture_output=True,
                        text=True,
                    )
                    geometry: dict[str, int] = {}
                    for line in win_info.stdout.strip().split("\n"):
                        if "=" in line:
                            key, val = line.split("=", 1)
                            geometry[key.upper()] = int(val)

                    name_info = subprocess.run(
                        ["xdotool", "getwindowname", wid],
                        capture_output=True,
                        text=True,
                    )

                    desktop = subprocess.run(
                        ["xdotool", "getwindowenv", wid, "_NET_WM_DESKTOP"],
                        capture_output=True,
                        text=True,
                    )

                    windows.append(
                        WindowState(
                            app_id=wid,
                            window_title=name_info.stdout.strip(),
                            x=geometry.get("X", 0),
                            y=geometry.get("Y", 0),
                            width=geometry.get("WIDTH", 100),
                            height=geometry.get("HEIGHT", 100),
                            workspace=int(desktop.stdout.strip()) if desktop.returncode == 0 else 0,
                        )
                    )
                except (subprocess.SubprocessError, ValueError, IndexError):
                    continue
        except FileNotFoundError:
            pass

    return windows


def _restore_window(window: WindowState) -> bool:
    """Restore a window to saved position."""
    try:
        subprocess.run(
            ["wmctl", "jr", "-w", window.app_id, "-x", str(window.x), "-y", str(window.y)],
            check=True,
        )
        return True
    except subprocess.SubprocessError:
        pass

    try:
        subprocess.run(
            [
                "xdotool",
                "windowmove",
                window.app_id,
                str(window.x),
                str(window.y),
            ],
            check=True,
        )
        subprocess.run(
            [
                "xdotool",
                "windowsize",
                window.app_id,
                str(window.width),
                str(window.height),
            ],
            check=True,
        )
        return True
    except (subprocess.SubprocessError, ValueError):
        error(f"Failed to restore window: {window.window_title}")
        return False


def save_snapshot(mode_name: str, dev_mode: bool = False) -> bool:
    """
    Save current window positions as a snapshot.

    Args:
        mode_name: Name of the mode to snapshot
        dev_mode: If True, don't save to disk

    Returns:
        True if successful
    """
    if dev_mode:
        info(f"[DEV] Would save snapshot for mode: {mode_name}")
        return True

    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    snapshot_file = SNAPSHOT_DIR / f"{mode_name}.yaml"

    windows = _get_window_list()

    if not windows:
        warning("No windows found to snapshot")

    import yaml

    with open(snapshot_file, "w") as f:
        yaml.dump([w.to_dict() for w in windows], f)

    info(f"Saved snapshot with {len(windows)} windows", mode=mode_name)
    return True


def load_snapshot(mode_name: str) -> list[WindowState] | None:
    """
    Load a saved snapshot.

    Args:
        mode_name: Name of the mode snapshot

    Returns:
        List of WindowStates if snapshot exists, None otherwise
    """
    snapshot_file = SNAPSHOT_DIR / f"{mode_name}.yaml"

    if not snapshot_file.exists():
        return None

    import yaml

    try:
        with open(snapshot_file, "r") as f:
            data = yaml.safe_load(f)
            return [WindowState.from_dict(w) for w in data]
    except (yaml.YAMLError, IOError, KeyError):
        return None


def restore_snapshot(mode_name: str, dev_mode: bool = False) -> bool:
    """
    Restore window positions from a snapshot.

    Args:
        mode_name: Name of the mode to restore
        dev_mode: If True, don't actually restore

    Returns:
        True if successful
    """
    if dev_mode:
        info(f"[DEV] Would restore snapshot for mode: {mode_name}")
        return True

    windows = load_snapshot(mode_name)

    if not windows:
        warning(f"No snapshot found for mode: {mode_name}")
        return False

    success = 0
    for window in windows:
        if _restore_window(window):
            success += 1

    info(f"Restored {success}/{len(windows)} windows", mode=mode_name)
    return success > 0


__all__ = [
    "WindowState",
    "save_snapshot",
    "load_snapshot",
    "restore_snapshot",
]