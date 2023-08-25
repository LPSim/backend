"""
Cards that can obtained in hands.
"""

from .event.others import Strategize
from .support import Supports


Cards = Strategize | Supports
