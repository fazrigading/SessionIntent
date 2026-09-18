"""
SessionIntent State Manager
Manages session state persistence (current mode, last session, etc.).
"""

from __future__ import annotations

from ..constants import STATE_FILE, STATE_DIR
from .log import info


def save_state(mode_name: str, dev_mode: bool = False) -> None:
    """
    Save the current mode as the active session state.

    Args:
        mode_name: Name of the current mode
        dev_mode: If True, don't actually write to disk
    """
    if dev_mode:
        print(f"[DEV] Would write state: {mode_name}")
        return

    # Ensure state directory exists
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    # Write state file
    with open(STATE_FILE, "w") as f:
        f.write(mode_name)

    info(f"State saved: {mode_name}")


def load_state() -> str | None:
    """
    Load the current session state (last active mode).

    Returns:
        Mode name if state exists, None otherwise
    """
    if not STATE_FILE.exists():
        return None

    try:
        with open(STATE_FILE, "r") as f:
            return f.read().strip()
    except (IOError, OSError):
        return None


def clear_state(dev_mode: bool = False) -> None:
    """
    Clear the current session state.

    Args:
        dev_mode: If True, don't actually delete the file
    """
    if dev_mode:
        print("[DEV] Would clear state")
        return

    if STATE_FILE.exists():
        try:
            STATE_FILE.unlink()
        except (IOError, OSError):
            pass


def get_current_state() -> str | None:
    """Alias for load_state()."""
    return load_state()


def state_exists() -> bool:
    """Check if a state file exists."""
    return STATE_FILE.exists()
