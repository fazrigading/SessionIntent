"""
SessionIntent Workspace Package
Provides GNOME workspace switching and management.
"""

from .manager import (
    switch_workspace,
    get_current_workspace,
    get_all_workspace_names,
    get_workspace_count,
)

__all__ = [
    "switch_workspace",
    "get_current_workspace",
    "get_all_workspace_names",
    "get_workspace_count",
]
