"""
SessionIntent Provider Interfaces
Abstract base classes and error types for desktop-environment providers.
"""

from __future__ import annotations

from typing import List, Protocol


class ProviderError(Exception):
    """Base exception for provider errors."""


class ToolNotFoundError(ProviderError):
    """Raised when a required external tool is not found."""


class OperationFailedError(ProviderError):
    """Raised when a provider operation fails."""


class WorkspaceProvider(Protocol):
    """Workspace switching and querying."""

    def switch_workspace(self, num: int, monitor: str | None = None) -> bool: ...
    def get_current_workspace(self) -> int | None: ...
    def get_workspace_count(self) -> int: ...
    def wait_for_workspace(self, target: int, timeout: float) -> bool: ...
    def wait_for_window(
        self, app_pattern: str, target_workspace: int, timeout: float
    ) -> bool: ...


class DisplayProvider(Protocol):
    """Mode selection and menu formatting."""

    def select_mode(self, modes: dict) -> str | None: ...
    def format_menu(self, modes: dict) -> list[str]: ...
    def find_selector(self) -> str | None: ...


class ExtensionProvider(Protocol):
    """Desktop extension management."""

    def enable(self, ext_id: str) -> tuple[bool, str]: ...
    def disable(self, ext_id: str) -> tuple[bool, str]: ...
    def list(self) -> List[str]: ...
    def get_info(self, ext_id: str) -> dict | None: ...
    def apply(self, config: dict) -> List[str]: ...
    def ensure(self) -> tuple[bool, str]: ...


__all__ = [
    "ProviderError",
    "ToolNotFoundError",
    "OperationFailedError",
    "WorkspaceProvider",
    "DisplayProvider",
    "ExtensionProvider",
]
