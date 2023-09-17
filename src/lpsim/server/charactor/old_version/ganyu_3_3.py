from typing import Literal, List

from ..charactor_base import PhysicalNormalAttackBase
from ...consts import DieColor
from ...struct import Cost
from ..cryo.ganyu import Ganyu as G_3_7
from ..cryo.ganyu import UndividedHeart as UH_3_7
from ..cryo.ganyu import CelestialShower as CS_3_7
from ..cryo.ganyu import FrostflakeArrow, TrailOftheQilin


class CelestialShower(CS_3_7):
    desc: str = (
        'Deals 1 Cryo DMG, deals 1 Piercing DMG to all opposing characters on '
        'standby, summons 1 Sacred Cryo Pearl.'
    )
    damage: int = 1
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 3,
        charge = 2
    )


class UndividedHeart_3_3(UH_3_7):
    desc: str = (
        'Combat Action: When your active character is Ganyu, equip this card. '
        'After Ganyu equips this card, immediately use Frostflake Arrow once. '
        'When your Ganyu, who has this card equipped, uses Frostflake Arrow: '
        'Cryo DMG dealt by this Skill +1 '
        'if this Skill has been used before during this match, the Piercing '
        'DMG dealt to all opposing characters on standby is changed to 3.'
    )
    version: Literal['3.3'] = '3.3'


class Ganyu_3_3(G_3_7):
    version: Literal['3.3'] = '3.3'
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | TrailOftheQilin | FrostflakeArrow 
        | CelestialShower
    ] = []
    talent: UndividedHeart_3_3 | None

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
