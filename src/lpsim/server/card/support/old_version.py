from typing import Literal

from ...struct import Cost
from .locations import JadeChamber as JC_4_0
from .companions import Katheryne as K_3_6
from .companions import ChefMao as CM_4_1
from .companions import Dunyarzad as D_4_1
from .items import NRE as NRE_4_1


class JadeChamber_3_3(JC_4_0):
    version: Literal['3.3']
    cost: Cost = Cost(same_dice_number = 1)


class Katheryne_3_3(K_3_6):
    version: Literal['3.3']
    cost: Cost = Cost(any_dice_number = 2)


class ChefMao_3_3(CM_4_1):
    desc: str = (
        'After playing a Food Event Card: Create 1 random Elemental Die. '
        '(Once per Round) '
    )
    version: Literal['3.3']
    limited_usage: int = 0


class Dunyarzad_3_7(D_4_1):
    desc: str = (
        'When playing a Companion Support Card: Spend 1 less Elemental Dice. '
        '(Once per Round) '
    )
    version: Literal['3.7']
    limited_usage: int = 0


class NRE_3_3(NRE_4_1):
    version: Literal['3.3']
    cost: Cost = Cost(any_dice_number = 2)


OldVersionLocations = JadeChamber_3_3 | JadeChamber_3_3
OldVersionCompanions = (
    Dunyarzad_3_7

    | Katheryne_3_3 | ChefMao_3_3
)
OldVersionItems = NRE_3_3 | NRE_3_3
