from typing import Any, Literal

from ...consts import SkillType

from ...modifiable_values import DamageIncreaseValue
from .base import RoundCharactorStatus, ShieldCharactorStatus


class UnmovableMountain(ShieldCharactorStatus):
    name: Literal['Unmovable Mountain'] = 'Unmovable Mountain'
    desc: str = '''Provides 2 Shield to protect the equipped charactor.'''
    version: Literal['3.5'] = '3.5'
    usage: int = 2
    max_usage: int = 2


class VermillionHereafter(RoundCharactorStatus):
    name: Literal['Vermillion Hereafter']
    desc: str = '''During this Round, character deals +1 Normal Attack DMG.'''
    version: Literal['4.0'] = '4.0'
    usage: int = 1
    max_usage: int = 1

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


ArtifactCharactorStatus = UnmovableMountain | VermillionHereafter
