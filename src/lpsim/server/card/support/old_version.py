from typing import Literal

from ...struct import Cost
from .locations import JadeChamber as JC_4_0
from .companions import Katheryne as K_3_6


class JadeChamber_3_3(JC_4_0):
    version: Literal['3.3']
    cost: Cost = Cost(same_dice_number = 1)


class Katheryne_3_3(K_3_6):
    version: Literal['3.3']
    cost: Cost = Cost(any_dice_number = 2)


OldVersionLocations = JadeChamber_3_3 | JadeChamber_3_3
OldVersionCompanions = Katheryne_3_3 | Katheryne_3_3
