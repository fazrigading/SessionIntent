"""
SessionIntent Workspace Package
Provides GNOME workspace switching and management.
"""

from .manager import (
    switch_workspace,
    get_current_workspace,
    get_workspace_count,
    ensure_extension,
    wait_for_window,
)

__all__ = [
    "switch_workspace",
    "get_current_workspace",
    "get_workspace_count",
    "ensure_extension",
    "wait_for_window",
]
