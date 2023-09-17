from typing import Any, List, Literal

from ....action import Actions

from ....struct import Cost
from .element_artifacts import SmallElementalArtifact as SEA_4_0
from .element_artifacts import BigElementalArtifact as BEA_4_0
from .gamblers import GamblersEarrings as GE_3_8
from .vermillion_shimenawa import ThunderingPoise as TP_4_0
from .vermillion_shimenawa import VermillionHereafter as VH_4_0
from .vermillion_shimenawa import CapriciousVisage as CV_4_0
from .vermillion_shimenawa import ShimenawasReminiscence as SR_4_0


class SmallElementalArtifact_3_3(SEA_4_0):
    version: Literal['3.3']
    cost: Cost = Cost(same_dice_number = 2)


class BigElementalArtifact_3_6(BEA_4_0):
    version: Literal['3.6']
    cost: Cost = Cost(any_dice_number = 3)


class BigElementalArtifact_3_3(BEA_4_0):
    version: Literal['3.3']
    cost: Cost = Cost(same_dice_number = 3)


class GamblersEarrings_3_3(GE_3_8):
    version: Literal['3.3']
    usage: int = 999

    def equip(self, match: Any) -> List[Actions]:
        """
        Equip this artifact. Reset usage.
        """
        self.usage = 999
        return []


# VermillionShimenawas
'''
    ThunderingPoise | VermillionHereafter
    | CapriciousVisage | ShimenawasReminiscence 
'''


class ThunderingPoise(TP_4_0):
    version: Literal['3.7']
    cost: Cost = Cost(same_dice_number = 2)


class VermillionHereafter(VH_4_0):
    version: Literal['3.7']
    cost: Cost = Cost(same_dice_number = 3)


class CapriciousVisage(CV_4_0):
    version: Literal['3.7']
    cost: Cost = Cost(same_dice_number = 2)


class ShimenawasReminiscence(SR_4_0):
    version: Literal['3.7']
    cost: Cost = Cost(same_dice_number = 3)


VermillionShimenawas_3_7 = (
    ThunderingPoise | VermillionHereafter
    | CapriciousVisage | ShimenawasReminiscence
)


OldVersionArtifacts = (
    VermillionShimenawas_3_7

    | BigElementalArtifact_3_6

    | GamblersEarrings_3_3 | SmallElementalArtifact_3_3 
    | BigElementalArtifact_3_3
)
