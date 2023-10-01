from typing import Any, Literal

from ...consts import IconType

from ...modifiable_values import DamageIncreaseValue
from .base import RoundTeamStatus, ShieldTeamStatus


class RebelliousShield(ShieldTeamStatus):
    name: Literal['Rebellious Shield'] = 'Rebellious Shield'
    desc: str = (
        'Grants 1 Shield point to defend your active charactor. '
        '(Can stack. Max 2 Points.)'
    )
    version: Literal['3.7'] = '3.7'
    usage: int = 1
    max_usage: int = 2


class MillennialMovementFarewellSong(RoundTeamStatus):
    name: Literal[
        'Millennial Movement: Farewell Song'
    ] = 'Millennial Movement: Farewell Song'
    desc: str = '''Your character deals +1 DMG.'''
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


WeaponTeamStatus = RebelliousShield | MillennialMovementFarewellSong
