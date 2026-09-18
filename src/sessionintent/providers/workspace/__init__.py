"""Workspace providers."""

from .ewmh import EwmhWorkspaceProvider
from .gnome import GnomeWorkspaceProvider

__all__ = ["EwmhWorkspaceProvider", "GnomeWorkspaceProvider"]
