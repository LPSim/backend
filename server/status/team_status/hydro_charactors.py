from typing import Any, Literal

from ...consts import DamageElementalType, SkillType

from ...modifiable_values import DamageMultiplyValue
from .base import DefendTeamStatus, ExtraAttackTeamStatus, UsageTeamStatus


class IllusoryBubble(UsageTeamStatus):
    """
    Team status generated by Mona.
    """
    name: Literal['Illusory Bubble'] = 'Illusory Bubble'
    desc: str = (
        'When dealing Skill DMG: Remove this status and double the DMG dealt '
        'for this instance.'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1

    def value_modifier_DAMAGE_MULTIPLY(
        self, value: DamageMultiplyValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageMultiplyValue:
        """
        Double damage when skill damage made.
        """
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, None
        ):
            # not this charactor use skill, not modify
            return value
        if self.usage > 0:
            value.damage *= 2
            assert mode == 'REAL'
            self.usage -= 1
        return value


class RainbowBladework(UsageTeamStatus, ExtraAttackTeamStatus):
    name: Literal['Rainbow Bladework'] = 'Rainbow Bladework'
    desc: str = 'After your character uses a Normal Attack: Deal 1 Hydro DMG.'
    version: Literal['3.6'] = '3.6'
    usage: int = 3
    max_usage: int = 3

    trigger_skill_type: SkillType | None = SkillType.NORMAL_ATTACK
    damage: int = 1
    damage_elemental_type: DamageElementalType = DamageElementalType.HYDRO
    decrease_usage: bool = True


class RainSword(DefendTeamStatus):
    name: Literal['Rain Sword'] = 'Rain Sword'
    desc: str = (
        'When your active character receives at least 3 DMG: '
        'Decrease DMG taken by 1.'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    min_damage_to_trigger: int = 3
    max_in_one_time: int = 1


HydroCharactorTeamStatus = IllusoryBubble | RainbowBladework | RainSword
