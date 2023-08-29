from typing import Literal

from ...consts import ObjectPositionType

from ...modifiable_values import DamageMultiplyValue
from .base import UsageTeamStatus


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
        self, value: DamageMultiplyValue, mode: Literal['TEST', 'REAL']
    ) -> DamageMultiplyValue:
        """
        Double damage when skill damage made.
        """
        if not self.position.check_position_valid(
            value.position, value.match,
            player_id_same = True, target_area = ObjectPositionType.CHARACTOR,
        ):
            # not from self position or not charactor skill
            return value
        if value.target_position.player_id == self.position.player_id:
            # attack self, not activate
            raise NotImplementedError('Not tested part')
            return value
        if self.usage > 0:
            value.damage *= 2
            assert mode == 'REAL'
            self.usage -= 1
        return value


HydroCharactorTeamStatus = IllusoryBubble | IllusoryBubble
