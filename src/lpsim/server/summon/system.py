from typing import Literal

from ...utils.class_registry import register_class
from .base import AttackerSummonBase
from ..consts import DamageElementalType


class BurningFlame_3_3(AttackerSummonBase):
    name: Literal['Burning Flame'] = 'Burning Flame'
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.PYRO
    damage: int = 1
    renew_type: Literal['ADD'] = 'ADD'


register_class(BurningFlame_3_3)
