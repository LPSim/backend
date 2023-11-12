from typing import List, Literal

from ..charactor_base import PhysicalNormalAttackBase

from ....utils.class_registry import register_class

from ...consts import DieColor
from ...struct import Cost
from .razor_3_8 import Awakening_4_2, Razor_3_8 as R_3_8
from .razor_3_8 import LightningFang as LF_3_8
from .razor_3_8 import ClawAndThunder


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


class Awakening_3_3(Awakening_4_2):
    desc: str = (
        'Combat Action: When your active character is Razor, equip this card. '
        'After Razor equips this card, immediately use Claw and Thunder once. '
        'After your Razor, who has this card equipped, uses Claw and Thunder: '
        '1 of your Electro characters gains 1 Energy. '
        '(Active Character prioritized)'
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 4
    )
    usage: int = 999
    max_usage: int = 999


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


register_class(Razor_3_3 | Awakening_3_3)
