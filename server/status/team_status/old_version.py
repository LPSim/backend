"""
Team status that with old version. Note the version should not be initialized
by default to avoid using it accidently.
"""

from typing import Any, List, Literal
from .base import ExtraAttackTeamStatus, UsageTeamStatus
from ...modifiable_values import DamageIncreaseValue
from ...consts import DamageElementalType, DamageType, SkillType
from ...event import AfterMakeDamageEventArguments
from ...action import RemoveObjectAction


class CatalyzingField_3_3(UsageTeamStatus):
    """
    Catalyzing field.
    """
    name: Literal['Catalyzing Field'] = 'Catalyzing Field'
    desc: str = (
        'When you deal Electro DMG or Pyro DMG to an opposing active '
        'charactor, DMG dealt +1.'
    )
    version: Literal['3.3']
    usage: int = 3
    max_usage: int = 3

    def value_modifier_DAMAGE_INCREASE(
            self, value: DamageIncreaseValue, match: Any,
            mode: Literal['TEST', 'REAL']) -> DamageIncreaseValue:
        """
        Increase damage for dendro or electro damages, and decrease usage.
        """
        if value.damage_type != DamageType.DAMAGE:
            # not damage, not modify
            return value
        if not self.position.check_position_valid(
            value.position, match, player_idx_same = True,
        ):
            # source not self, not activate
            return value
        if not self.position.check_position_valid(
            value.target_position, match, 
            player_idx_same = False, target_is_active_charactor = True,
        ):
            # target not enemy, or target not active charactor, not activate
            return value
        if value.damage_elemental_type in [
            DamageElementalType.DENDRO,
            DamageElementalType.ELECTRO,
        ] and self.usage > 0:
            value.damage += 1
            assert mode == 'REAL'
            self.usage -= 1
        return value

    def event_handler_MAKE_DAMAGE(
        self, event: AfterMakeDamageEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        """
        When damage made, check whether the round status should be removed.
        Not trigger on AFTER_MAKE_DAMAGE because when damage made, run out
        of usage, but new one is generated, should remove first then generate
        new one, otherwise newly updated status will be removed.
        """
        return self.check_should_remove()


class RainbowBladework_3_3(UsageTeamStatus, ExtraAttackTeamStatus):
    name: Literal['Rainbow Bladework'] = 'Rainbow Bladework'
    desc: str = 'After your character uses a Normal Attack: Deal 1 Hydro DMG.'
    version: Literal['3.3']
    usage: int = 3
    max_usage: int = 3

    trigger_skill_type: SkillType | None = SkillType.NORMAL_ATTACK
    damage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.HYDRO
    decrease_usage: bool = True


OldVersionTeamStatus = CatalyzingField_3_3 | RainbowBladework_3_3
