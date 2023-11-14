from typing import Literal, List

from ....utils.class_registry import register_class

from ..charactor_base import PhysicalNormalAttackBase
from ...consts import DieColor
from ...struct import Cost
from .ganyu_3_7 import Ganyu_3_7 as G_3_7
from .ganyu_3_7 import UndividedHeart_3_7 as UH_3_7
from .ganyu_3_7 import CelestialShower as CS_3_7
from .ganyu_3_7 import FrostflakeArrow, TrailOftheQilin


class CelestialShower(CS_3_7):
    damage: int = 1
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 3,
        charge = 2
    )


class UndividedHeart_3_3(UH_3_7):
    version: Literal['3.3'] = '3.3'


class Ganyu_3_3(G_3_7):
    version: Literal['3.3'] = '3.3'
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | TrailOftheQilin | FrostflakeArrow 
        | CelestialShower
    ] = []

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Liutian Archery',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            TrailOftheQilin(),
            FrostflakeArrow(),
            CelestialShower()
        ]


register_class(Ganyu_3_3 | UndividedHeart_3_3)
