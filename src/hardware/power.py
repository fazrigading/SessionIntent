"""
SessionIntent Hardware Power Detection
Detects whether the system is running on AC power or battery.
"""

import os


def is_on_ac() -> bool:
    """
    Check if the system is running on AC power.

    Returns:
        True if on AC power (plugged in), False if on battery.
        Defaults to True if power detection fails.
    """
    try:
        if os.path.exists(_AC_PATH):
            with open(_AC_PATH, "r") as f:
                return f.read().strip() == "1"
    except (IOError, OSError):
        pass

    # Default to AC if detection fails
    return True


# AC path (module-level for easier testing)
_AC_PATH = "/sys/class/power_supply/AC/online"
