from typing import List, Literal

from ....utils.class_registry import register_class

from ..charactor_base import PhysicalNormalAttackBase
from .shenhe_3_7 import (
    Shenhe_3_7, SpringSpiritSummoning as SS_3_7, DivineMaidensDeliverance
)


class SpringSpiritSummoning(SS_3_7):
    max_usage: int = 2


class Shenhe_4_2(Shenhe_3_7):
    version: Literal['4.2'] = '4.2'
    skills: List[
        PhysicalNormalAttackBase | SpringSpiritSummoning 
        | DivineMaidensDeliverance
    ] = []

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Dawnstar Piercer',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            SpringSpiritSummoning(),
            DivineMaidensDeliverance(),
        ]


register_class(Shenhe_4_2)
