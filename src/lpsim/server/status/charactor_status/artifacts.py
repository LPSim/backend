from typing import Any, Literal

from ....utils.class_registry import register_class

from ...consts import IconType, SkillType

from ...modifiable_values import DamageIncreaseValue
from .base import RoundCharactorStatus, ShieldCharactorStatus


class UnmovableMountain_3_5(ShieldCharactorStatus):
    name: Literal['Unmovable Mountain'] = 'Unmovable Mountain'
    version: Literal['3.5'] = '3.5'
    usage: int = 2
    max_usage: int = 2


class VermillionHereafter_4_0(RoundCharactorStatus):
    name: Literal['Vermillion Hereafter']
    version: Literal['4.0'] = '4.0'
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.ATK_UP] = IconType.ATK_UP

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, SkillType.NORMAL_ATTACK
        ):
            # not current charactor using normal attack
            return value
        # increase damage
        assert mode == 'REAL'
        value.damage += 1
        return value


register_class(UnmovableMountain_3_5 | VermillionHereafter_4_0)
