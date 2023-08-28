"""
Team status that with old version. Note the version should not be initialized
by default to avoid using it accidently.
"""

from typing import List, Literal
from .base import UsageTeamStatus
from ...modifiable_values import DamageIncreaseValue
from ...consts import DamageElementalType
from ...event import AfterMakeDamageEventArguments
from ...action import Actions


class CatalyzingField(UsageTeamStatus):
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
            self, value: DamageIncreaseValue,
            mode: Literal['TEST', 'REAL']) -> DamageIncreaseValue:
        """
        Increase damage for dendro or electro damages, and decrease usage.
        """
        if not self.position.check_position_valid(
            value.position, value.match, player_id_same = True,
        ):
            # source not self, not activate
            return value
        if not self.position.check_position_valid(
            value.target_position, value.match, 
            player_id_same = False, target_is_active_charactor = True,
        ):
            # target not enemy, or target not active charactor, not activate
            return value
        if value.damage_elemental_type in [
            DamageElementalType.DENDRO,
            DamageElementalType.ELECTRO,
        ] and self.usage > 0:
            value.damage += 1
            if mode == 'REAL':
                self.usage -= 1
        return value

    def event_handler_MAKE_DAMAGE(
            self, event: AfterMakeDamageEventArguments) -> List[Actions]:
        """
        When damage made, check whether the round status should be removed.
        Not trigger on AFTER_MAKE_DAMAGE because when damage made, run out
        of usage, but new one is generated, should remove first then generate
        new one, otherwise newly updated status will be removed.
        """
        return self.check_remove_triggered()


OldVersionTeamStatus = CatalyzingField | CatalyzingField
