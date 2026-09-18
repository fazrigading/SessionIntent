"""Extension providers."""

from .gnome import GnomeExtensionProvider, NullExtensionProvider
from .kde import KdeExtensionProvider

__all__ = ["GnomeExtensionProvider", "KdeExtensionProvider", "NullExtensionProvider"]
