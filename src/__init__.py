"""
SessionIntent Package
Session orchestration for GNOME Wayland.
"""

from .session import SessionManager
from .config import load_config, load_apps, init_default_configs
from .hardware import is_on_ac
from .ui import select_mode
from .workspace import switch_workspace
from .app import launch_app, is_running
from .extensions import apply_extensions, resolve_extension_id
from .plugins import get_plugin_manager

__version__ = "0.3.3"
__all__ = [
    "SessionManager",
    "load_config",
    "load_apps",
    "init_default_configs",
    "is_on_ac",
    "select_mode",
    "switch_workspace",
    "launch_app",
    "is_running",
    "apply_extensions",
    "resolve_extension_id",
    "get_plugin_manager",
]
