"""
SessionIntent Paths
All path constants are defined here for easy configuration.
"""

import pathlib
import os

# Directories
CONFIG_DIR = pathlib.Path.home() / ".config" / "sessionintent"
SYSTEM_CONFIG_DIR = pathlib.Path("/usr/share/sessionintent")
STATE_DIR = (
    pathlib.Path(
        os.environ.get("XDG_STATE_HOME", pathlib.Path.home() / ".local" / "state")
    )
    / "sessionintent"
)

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
