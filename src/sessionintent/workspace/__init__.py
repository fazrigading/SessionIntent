"""
SessionIntent Workspace Package
Compatibility re-exports; new code should use sessionintent.providers.
"""

from ..providers.workspace.ewmh import EwmhWorkspaceProvider, wait_for_window
from ..providers.workspace.gnome import (
    GnomeWorkspaceProvider,
    ensure_extension,
    get_current_workspace,
    get_workspace_count,
    switch_workspace,
    wait_for_workspace,
)

__all__ = [
    "EwmhWorkspaceProvider",
    "GnomeWorkspaceProvider",
    "ensure_extension",
    "get_current_workspace",
    "get_workspace_count",
    "switch_workspace",
    "wait_for_window",
    "wait_for_workspace",
]
