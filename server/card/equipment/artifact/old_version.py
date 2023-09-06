from typing import Any, List, Literal

from ....action import Actions

from ....struct import Cost
from .element_artifacts import SmallElementalArtifact as SEA_4_0
from .others import GamblersEarrings as GE_3_8


class SmallElementalArtifact_3_3(SEA_4_0):
    version: Literal['3.3']
    cost: Cost = Cost(same_dice_number = 2)


class GamblersEarrings_3_3(GE_3_8):
    version: Literal['3.3']
    usage: int = 999

    def equip(self, match: Any) -> List[Actions]:
        """
        Equip this artifact. Reset usage.
        """
        self.usage = 999
        return []


OldVersionArtifacts = SmallElementalArtifact_3_3 | GamblersEarrings_3_3
