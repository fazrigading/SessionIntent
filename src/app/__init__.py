"""
SessionIntent App Package
Provides application management (registry, launching, templates).
"""

from .registry import AppRegistry, get_registry
from .controller import is_running, launch_app
from .template import (
    resolve_template,
    extract_template_vars,
    is_template,
    resolve_if_template,
)

__all__ = [
    # Registry
    "AppRegistry",
    "get_registry",
    # Controller
    "is_running",
    "launch_app",
    # Template
    "resolve_template",
    "extract_template_vars",
    "is_template",
    "resolve_if_template",
]
