from typing import List, Literal

from ..charactor_base import PhysicalNormalAttackBase
from ...struct import Cost
from ...consts import DieColor
from ..electro.beidou import Beidou as Beidou_3_8
from ..electro.beidou import Wavestrider as Wavestrider_3_8
from ..electro.beidou import Stormbreaker as Stormbreaker_3_8
from ..electro.beidou import Tidecaller


class Wavestrider(Wavestrider_3_8):
    damage: int = 2


class Stormbreaker(Stormbreaker_3_8):
    damage: int = 3
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 4,
        charge = 3
    )


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
