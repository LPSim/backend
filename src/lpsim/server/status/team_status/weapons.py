from typing import Any, Literal

from ....utils.class_registry import register_class

from ...consts import IconType

from ...modifiable_values import DamageIncreaseValue
from .base import RoundTeamStatus, ShieldTeamStatus


class RebelliousShield_3_7(ShieldTeamStatus):
    name: Literal['Rebellious Shield'] = 'Rebellious Shield'
    version: Literal['3.7'] = '3.7'
    usage: int = 1
    max_usage: int = 2


class MillennialMovementFarewellSong_3_7(RoundTeamStatus):
    name: Literal[
        'Millennial Movement: Farewell Song'
    ] = 'Millennial Movement: Farewell Song'
    version: Literal['3.7'] = '3.7'
    usage: int = 2
    max_usage: int = 2
    icon_type: Literal[IconType.ATK_UP] = IconType.ATK_UP

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        if value.is_corresponding_charactor_use_damage_skill(
            self.position, match, None
        ):
            assert mode == 'REAL'
            value.damage += 1
        return value


register_class(RebelliousShield_3_7 | MillennialMovementFarewellSong_3_7)
