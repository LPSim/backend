from typing import List, Literal

from ....utils.class_registry import register_class

from ...consts import DieColor

from ...struct import Cost

from .xiangling_3_8 import Crossfire_4_2, Xiangling_3_8 as X_3_8
from .xiangling_3_8 import Pyronado as P_3_8
from .xiangling_3_8 import DoughFu, GuobaAttack


class Pyronado(P_3_8):
    damage: int = 2


class Crossfire_3_3(Crossfire_4_2):
    version: Literal['3.3']
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 4
    )


class Xiangling_3_3(X_3_8):
    version: Literal['3.3']
    skills: List[DoughFu | GuobaAttack | Pyronado] = []

    def _init_skills(self) -> None:
        self.skills = [
            DoughFu(),
            GuobaAttack(),
            Pyronado()
        ]


register_class(Xiangling_3_3 | Crossfire_3_3)
