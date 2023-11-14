from typing import List, Literal

from ....utils.class_registry import register_class

from ..charactor_base import PhysicalNormalAttackBase

from ...consts import DieColor

from ...struct import Cost
from .jean_3_3 import (
    Jean_3_3, DandelionField_3_3, LandsOfDandelion_3_3, GaleBlade,
    DandelionBreeze as DB_3_3
)


class DandelionField_4_2(DandelionField_3_3):
    version: Literal['4.2'] = '4.2'
    damage: int = 1


class LandsOfDandelion_4_2(LandsOfDandelion_3_3):
    version: Literal['4.2'] = '4.2'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 4,
        charge = 2
    )


class DandelionBreeze(DB_3_3):
    version: Literal['4.2'] = '4.2'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 4,
        charge = 2
    )


class Jean_4_2(Jean_3_3):
    version: Literal['4.2'] = '4.2'
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | GaleBlade | DandelionBreeze
    ] = []

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Favonius Bladework',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            GaleBlade(),
            DandelionBreeze(),
        ]


register_class(Jean_4_2 | DandelionField_4_2 | LandsOfDandelion_4_2)
