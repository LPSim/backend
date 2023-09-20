from typing import List, Literal

from ..charactor_base import PhysicalNormalAttackBase
from ...consts import DieColor
from ...struct import Cost
from ..electro.razor import Razor as R_3_8
from ..electro.razor import LightningFang as LF_3_8
from ..electro.razor import ClawAndThunder


class LightningFang(LF_3_8):
    desc: str = (
        'Deals 5 Electro DMG. This character gains The Wolf Within.'
    )
    damage: int = 5
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3,
        charge = 3
    )


class Razor_3_3(R_3_8):
    version: Literal['3.3']
    skills: List[
        PhysicalNormalAttackBase | ClawAndThunder | LightningFang
    ] = []
    max_charge: int = 3

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Steel Fang',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            ClawAndThunder(),
            LightningFang()
        ]
