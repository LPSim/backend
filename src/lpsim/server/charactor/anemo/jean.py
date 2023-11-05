from typing import List, Literal

from ..charactor_base import PhysicalNormalAttackBase

from ...consts import DieColor

from ...struct import Cost
from ..old_version.jean_3_3 import (
    Jean_3_3, DandelionField_3_3, LandsOfDandelion_3_3, GaleBlade,
    DandelionBreeze as DB_3_3
)


class DandelionField(DandelionField_3_3):
    desc: str = (
        'End Phase: Deal 1 Anemo DMG, heal your active character for 1 HP.'
    )
    version: Literal['4.2'] = '4.2'
    damage: int = 1


class LandsOfDandelion(LandsOfDandelion_3_3):
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


class Jean(Jean_3_3):
    version: Literal['4.2'] = '4.2'
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | GaleBlade | DandelionBreeze
    ] = []
    talent: LandsOfDandelion | None = None

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Favonius Bladework',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            GaleBlade(),
            DandelionBreeze(),
        ]
