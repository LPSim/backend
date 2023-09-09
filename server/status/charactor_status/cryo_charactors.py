
from typing import Any, Literal

from ...consts import SkillType

from ...modifiable_values import DamageIncreaseValue
from .base import UsageCharactorStatus


class Grimheart(UsageCharactorStatus):
    name: Literal['Grimheart'] = 'Grimheart'
    desc: str = (
        'After the character to which this is attached uses Icetide Vortex: '
        'Remove this status, DMG +_DAMAGE_ for this instance.'
    )
    version: Literal['3.8'] = '3.8'
    damage: int = 3
    usage: int = 1
    max_usage: int = 1

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self.version == '3.5':
            self.damage = 2
        else:
            assert self.version == '3.8'
            self.damage = 3
        self.desc = self.desc.replace('_DAMAGE_', str(self.damage))

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> DamageIncreaseValue:
        """
        When character uses Icetide Vortex, increase damage by self.damage
        """
        if value.damage_from_element_reaction:
            # from element reaction, do nothing
            return value
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, SkillType.ELEMENTAL_SKILL
        ):
            # not self use elemental skill, do nothing
            return value
        assert self.usage > 0
        assert mode == 'REAL'
        self.usage -= 1
        value.damage += self.damage
        return value


CryoCharactorStatus = Grimheart | Grimheart
