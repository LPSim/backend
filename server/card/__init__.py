"""
Cards that can obtained in hands.
"""

from .event import EventCards
from .support import Supports
from .equipment.artifact import Artifacts


Cards = EventCards | Supports | Artifacts
