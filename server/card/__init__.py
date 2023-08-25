"""
Cards that can obtained in hands.
"""

from .event.others import Strategize
from .support import Supports
from .equipment.artifact import Artifacts


Cards = Strategize | Supports | Artifacts
