from typing import Literal

from ...struct import Cost
from .locations import JadeChamber as JC_4_0


class JadeChamber(JC_4_0):
    version: Literal['3.3']
    cost: Cost = Cost(same_dice_number = 1)


OldVersionLocations = JadeChamber | JadeChamber
