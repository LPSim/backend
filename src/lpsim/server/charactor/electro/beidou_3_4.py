from typing import List, Literal

from ....utils.class_registry import register_class

from ..charactor_base import PhysicalNormalAttackBase
from ...struct import Cost
from ...consts import DieColor
from .beidou_3_8 import Beidou_3_8 as Beidou_3_8, LightningStorm_4_2
from .beidou_3_8 import Wavestrider as Wavestrider_3_8
from .beidou_3_8 import Stormbreaker as Stormbreaker_3_8
from .beidou_3_8 import Tidecaller


class Wavestrider(Wavestrider_3_8):
    damage: int = 2


class Stormbreaker(Stormbreaker_3_8):
    damage: int = 3
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 4,
        charge = 3
    )


class LightningStorm_3_4(LightningStorm_4_2):
    version: Literal['3.4'] = '3.4'
    need_to_activate: bool = True


class Beidou_3_4(Beidou_3_8):
    version: Literal['3.4']
    skills: List[
        PhysicalNormalAttackBase | Tidecaller | Wavestrider | Stormbreaker
    ] = []

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Oceanborne',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            Tidecaller(),
            Wavestrider(),
            Stormbreaker(),
        ]


register_class(Beidou_3_4 | LightningStorm_3_4)
