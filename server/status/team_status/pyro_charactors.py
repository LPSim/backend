from typing import Any, List, Literal

from ...struct import Cost

from ...modifiable_values import DamageValue

from ...consts import DamageElementalType, DamageType, ObjectPositionType

from ...action import MakeDamageAction

from ...event import SkillEndEventArguments
from .base import UsageTeamStatus


class SparksNSplash(UsageTeamStatus):
    name: Literal["Sparks 'n' Splash"] = "Sparks 'n' Splash"
    desc: str = (
        "After a character to which Sparks 'n' Splash is attached uses a "
        "Skill: Deals 2 Pyro DMG to their team's active character. Usage(s): 2"
    )
    version: Literal['3.4'] = '3.4'
    usage: int = 2
    max_usage: int = 2

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        When attached charactor use skill, then damage itself.
        """
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True, 
            target_area = ObjectPositionType.SKILL,
        ):
            # not charactor use skill, not modify
            return []
        active_charactor = match.player_tables[
            self.position.player_idx].get_active_charactor()
        if self.usage > 0:  # pragma: no branch
            self.usage -= 1
            return [MakeDamageAction(
                source_player_idx = self.position.player_idx,
                target_player_idx = self.position.player_idx,
                damage_value_list = [DamageValue(
                    position = self.position,
                    damage_type = DamageType.DAMAGE,
                    target_position = active_charactor.position,
                    damage = 2,
                    damage_elemental_type = DamageElementalType.PYRO,
                    cost = Cost()
                )]
            )]
        else:
            return []  # pragma: no cover


PyroTeamStatus = SparksNSplash | SparksNSplash
