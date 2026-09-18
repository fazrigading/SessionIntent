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
from .detect import BACKENDS, DesktopProfile, detect_desktop, get_providers

__all__ = [
    "BACKENDS",
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
