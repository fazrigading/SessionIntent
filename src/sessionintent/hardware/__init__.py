"""
SessionIntent Hardware Package
Provides hardware state detection (AC/battery, etc.).
"""

from .power import is_on_ac

__all__ = ["is_on_ac"]
