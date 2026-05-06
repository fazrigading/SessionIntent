"""
SessionIntent App Package
Provides application management (registry, launching, templates, detection).
"""

from .registry import AppRegistry, get_registry
from .controller import is_running, launch_app, launch_apps_async
from .template import (
    resolve_template,
    extract_template_vars,
    is_template,
    resolve_if_template,
)
from .detect import detect_all_apps, get_categorized_apps, get_category_list
from .setup import setup_interactive, rescan_options

__all__ = [
    # Registry
    "AppRegistry",
    "get_registry",
    # Controller
    "is_running",
    "launch_app",
    "launch_apps_async",
    # Template
    "resolve_template",
    "extract_template_vars",
    "is_template",
    "resolve_if_template",
    # Detection
    "detect_all_apps",
    "get_categorized_apps",
    "get_category_list",
    # Setup
    "setup_interactive",
    "rescan_options",
]
