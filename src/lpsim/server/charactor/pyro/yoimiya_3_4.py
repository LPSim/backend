from typing import List, Literal

from ....utils.class_registry import register_class
from ...consts import DieColor
from ...struct import Cost
from .yoimiya_3_8 import Yoimiya_3_8 as Y_3_8
from .yoimiya_3_8 import RyuukinSaxifrage as RS_3_8
from .yoimiya_3_8 import FireworkFlareUp, NiwabiFireDance


class RyuukinSaxifrage(RS_3_8):
    damage: int = 4
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 4,
        charge = 3
    )


class Yoimiya_3_4(Y_3_8):
    version: Literal['3.4']
    skills: List[FireworkFlareUp | NiwabiFireDance | RyuukinSaxifrage] = []

    def _init_skills(self) -> None:
        self.skills = [
            FireworkFlareUp(),
            NiwabiFireDance(),
            RyuukinSaxifrage()
        ]


register_class(Yoimiya_3_4)
