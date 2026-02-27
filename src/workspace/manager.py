"""
SessionIntent Workspace Manager
Provides GNOME workspace switching via gdbus.
"""

from __future__ import annotations

import subprocess
import time


def switch_workspace(workspace_num: int, dev_mode: bool = False) -> None:
    """
    Switch to the specified workspace.

    Args:
        workspace_num: 1-indexed workspace number
        dev_mode: If True, print commands instead of executing
    """
    if dev_mode:
        print(f"[DEV] Switching to workspace {workspace_num}")
        return

    idx = workspace_num - 1  # Convert to 0-indexed

    cmd = [
        "gdbus",
        "call",
        "--session",
        "--dest",
        "org.gnome.Shell",
        "--object-path",
        "/org/gnome/Shell",
        "--method",
        "org.gnome.Shell.Eval",
        f"Main.wm.actionMoveWorkspace(Main.wm.get_workspace_by_index({idx}))",
    ]

    try:
        subprocess.run(cmd, capture_output=True, check=True)
        time.sleep(0.5)  # Wait for workspace to switch
    except subprocess.CalledProcessError as e:
        print(f"Workspace error: {e}")
    except Exception as e:
        print(f"Workspace error: {e}")


def get_current_workspace(dev_mode: bool = False) -> int | None:
    """
    Get the current workspace number (1-indexed).

    Note: This requires GNOME Shell API access which may not be available
    in all environments. Returns None if detection fails.

    Args:
        dev_mode: If True, return 1

    Returns:
        1-indexed workspace number, or None if not available
    """
    if dev_mode:
        return 1

    cmd = [
        "gdbus",
        "call",
        "--session",
        "--dest",
        "org.gnome.Shell",
        "--object-path",
        "/org/gnome/Shell",
        "--method",
        "org.gnome.Shell.Eval",
        "Main.wm.get_active_workspace_index()",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # Output format: (uint32 N,)
        output = result.stdout.strip()
        import re

        match = re.search(r"uint32\s+(\d+)", output)
        if match:
            return int(match.group(1)) + 1  # Convert to 1-indexed
    except (subprocess.CalledProcessError, Exception):
        pass

    return None


def get_all_workspace_names(dev_mode: bool = False) -> list[str]:
    """
    Get names of all workspaces.

    Returns empty list if detection fails.

    Args:
        dev_mode: If True, return ["Workspace 1"]

    Returns:
        List of workspace names
    """
    if dev_mode:
        return ["Workspace 1"]

    cmd = [
        "gdbus",
        "call",
        "--session",
        "--dest",
        "org.gnome.Shell",
        "--object-path",
        "/org/gnome/Shell",
        "--method",
        "org.gnome.Shell.Eval",
        "Main.wm._workspaces.map(w => w.name)",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        import re

        # Extract array content
        match = re.search(r"\[(.*?)\]", result.stdout)
        if match:
            names_str = match.group(1)
            # Simple parsing - quotes removed
            names = [n.strip().strip("\"'") for n in names_str.split(",")]
            return [n for n in names if n]
    except (subprocess.CalledProcessError, Exception):
        pass

    return []


def get_workspace_count(dev_mode: bool = False) -> int:
    """
    Get the total number of workspaces.

    Args:
        dev_mode: If True, return 1

    Returns:
        Number of workspaces
    """
    if dev_mode:
        return 1

    cmd = [
        "gdbus",
        "call",
        "--session",
        "--dest",
        "org.gnome.Shell",
        "--object-path",
        "/org/gnome/Shell",
        "--method",
        "org.gnome.Shell.Eval",
        "Main.wm._workspaces.length",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        import re

        match = re.search(r"uint32\s+(\d+)", result.stdout)
        if match:
            return int(match.group(1))
    except (subprocess.CalledProcessError, Exception):
        pass

    return 1  # Default to 1 workspace
