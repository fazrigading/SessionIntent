"""
SessionIntent Providers Package
Desktop-environment providers plus detection and factory.
"""

from .base import (
    DisplayProvider,
    ExtensionProvider,
    OperationFailedError,
    ProviderError,
    ToolNotFoundError,
    WorkspaceProvider,
)
from .detect import DesktopProfile, detect_desktop, get_providers

__all__ = [
    "DesktopProfile",
    "DisplayProvider",
    "ExtensionProvider",
    "OperationFailedError",
    "ProviderError",
    "ToolNotFoundError",
    "WorkspaceProvider",
    "detect_desktop",
    "get_providers",
]
