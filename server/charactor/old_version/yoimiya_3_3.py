from typing import List, Literal
from ...consts import DieColor
from ...struct import Cost
from ..pyro.yoimiya import Yoimiya as Y_3_8
from ..pyro.yoimiya import RyuukinSaxifrage as RS_3_8
from ..pyro.yoimiya import FireworkFlareUp, NiwabiFireDance


class RyuukinSaxifrage(RS_3_8):
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 3,
        charge = 2
    )


class Yoimiya_3_3(Y_3_8):
    version: Literal['3.3']
    max_charge: int = 2
    skills: List[FireworkFlareUp | NiwabiFireDance | RyuukinSaxifrage] = []

    def _init_skills(self) -> None:
        self.skills = [
            FireworkFlareUp(),
            NiwabiFireDance(),
            RyuukinSaxifrage()
        ]
