from .base import SummonBase, AttackerSummonBase
from .system import BurningFlame


Summons = SummonBase | AttackerSummonBase | BurningFlame
