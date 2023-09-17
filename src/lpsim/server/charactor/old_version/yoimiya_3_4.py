from typing import List, Literal
from ...consts import DieColor
from ...struct import Cost
from ..pyro.yoimiya import Yoimiya as Y_3_8
from ..pyro.yoimiya import RyuukinSaxifrage as RS_3_8
from ..pyro.yoimiya import FireworkFlareUp, NiwabiFireDance


class RyuukinSaxifrage(RS_3_8):
    damage: int = 4
    desc: str = '''Deals 4 Pyro DMG, creates 1 Aurous Blaze.'''
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
