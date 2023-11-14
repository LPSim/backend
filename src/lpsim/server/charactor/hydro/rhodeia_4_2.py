from typing import List, Literal

from ...consts import ELEMENT_TO_DAMAGE_TYPE

from ....utils.class_registry import register_class

from ..charactor_base import ElementalNormalAttackBase
from .rhodeia_3_3 import (
    RhodeiaOfLoch_3_3, RhodeiaElementSkill, TideAndTorrent as TAT_3_3
)


class TideAndTorrent(TAT_3_3):
    damage: int = 4
    damage_per_summon: int = 1


class RhodeiaOfLoch_4_2(RhodeiaOfLoch_3_3):
    version: Literal['4.2'] = '4.2'
    skills: List[
        ElementalNormalAttackBase
        | RhodeiaElementSkill | TideAndTorrent
    ] = []

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name = 'Surge',
                damage_type = ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost = ElementalNormalAttackBase.get_cost(self.element),
            ),
            RhodeiaElementSkill(
                name = 'Oceanid Mimic Summoning',
            ),
            RhodeiaElementSkill(
                name = 'The Myriad Wilds',
            ),
            TideAndTorrent(),
        ]


register_class(RhodeiaOfLoch_4_2)
