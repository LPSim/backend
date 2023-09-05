from typing import Any, Literal

from ...consts import DamageElementalType

from ...modifiable_values import DamageElementEnhanceValue, DamageIncreaseValue
from .base import DefendCharactorStatus


class Stealth(DefendCharactorStatus):
    name: Literal['Stealth'] = 'Stealth'
    desc: str = (
        'The character to which this is attached takes -1 DMG and '
        'deals +1 DMG. Usage(s): 2'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    min_damage_to_trigger: int = 1
    max_in_one_time: int = 1

    def value_modifier_DAMAGE_ELEMENT_ENHANCE(
        self, value: DamageElementEnhanceValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageElementEnhanceValue:
        """
        When self use skill, and has talent, change physical to pyro
        """
        assert mode == 'REAL'
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, None
        ):
            # not corresponding charactor use skill, do nothing
            return value
        if self.usage <= 0:  # pragma: no cover
            # no usage, do nothing
            return value
        charactor = match.player_tables[
            self.position.player_idx].charactors[self.position.charactor_idx]
        if charactor.talent is None:
            # no talent, do nothing
            return value
        # change physical to pyro
        if value.damage_elemental_type == DamageElementalType.PHYSICAL:
            value.damage_elemental_type = DamageElementalType.PYRO
        return value

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        """
        When self use skill, increase damage by 1
        """
        assert mode == 'REAL'
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, None
        ):
            # not corresponding charactor use damage skill, do nothing
            return value
        if self.usage <= 0:  # pragma: no cover
            # no usage, do nothing
            return value
        # increase damage by 1
        value.damage += 1
        self.usage -= 1
        return value


PyroCharactorStatus = Stealth | Stealth
