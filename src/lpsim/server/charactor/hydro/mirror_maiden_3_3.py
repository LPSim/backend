from typing import List, Literal

from ....utils.class_registry import register_class

from ...consts import ELEMENT_TO_DAMAGE_TYPE

from ..charactor_base import ElementalBurstBase, ElementalNormalAttackBase
from .mirror_maiden_3_7 import MirrorMaiden_3_7 as MM_3_7
from .mirror_maiden_3_7 import InfluxBlast as IB_3_7


class InfluxBlast(IB_3_7):
    damage: int = 3


class MirrorMaiden_3_3(MM_3_7):
    version: Literal['3.3']
    skills: List[
        ElementalNormalAttackBase | InfluxBlast | ElementalBurstBase
    ] = []

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name = 'Water Ball',
                damage_type = ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost = ElementalNormalAttackBase.get_cost(self.element),
            ),
            InfluxBlast(),
            ElementalBurstBase(
                name = 'Rippled Reflection',
                damage = 5,
                damage_type = ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost = ElementalBurstBase.get_cost(self.element, 3, 2)
            )
        ]


register_class(MirrorMaiden_3_3)
