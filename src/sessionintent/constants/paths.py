"""
SessionIntent Paths
All path constants are defined here for easy configuration.
"""

import pathlib
import os


def _xdg_dir(env_var: str, fallback: pathlib.Path) -> pathlib.Path:
    """Resolve an XDG base directory (empty counts as unset per spec)."""
    override = os.environ.get(env_var)
    if override:
        return pathlib.Path(override)
    return fallback


XDG_CONFIG_HOME = _xdg_dir("XDG_CONFIG_HOME", pathlib.Path.home() / ".config")
XDG_STATE_HOME = _xdg_dir(
    "XDG_STATE_HOME", pathlib.Path.home() / ".local" / "state"
)

# Directories
CONFIG_DIR = XDG_CONFIG_HOME / "sessionintent"
SYSTEM_CONFIG_DIR = pathlib.Path("/usr/share/sessionintent")
STATE_DIR = XDG_STATE_HOME / "sessionintent"

# Config files
CONFIG_PATH = CONFIG_DIR / "config.yaml"
SYSTEM_CONFIG_PATH = SYSTEM_CONFIG_DIR / "config.yaml"
APPS_PATH = CONFIG_DIR / "apps.yaml"
SYSTEM_APPS_PATH = SYSTEM_CONFIG_DIR / "apps.yaml"

# State file
STATE_FILE = STATE_DIR / "current"

# Log file
LOG_DIR = STATE_DIR
LOG_FILE = LOG_DIR / "sessionintent.log"

# Power supply path
AC_PATH = "/sys/class/power_supply/AC/online"
