from typing import Any, List, Literal

from ...event import (
    ChooseCharactorEventArguments, SwitchCharactorEventArguments
)

from ...struct import Cost

from ...consts import DamageElementalType, DamageType

from ...modifiable_values import DamageValue

from ...action import MakeDamageAction
from .base import UsageTeamStatus


class Icicle(UsageTeamStatus):
    name: Literal['Icicle'] = 'Icicle'
    desc: str = '''After you switch characters: Deal 2 Cryo DMG. Usage(s): 3'''
    version: Literal['3.3'] = '3.3'
    usage: int = 3
    max_usage: int = 3

    def _attack(self, match: Any) -> List[MakeDamageAction]:
        """
        attack enemy active charactor
        """
        if self.usage <= 0:  # pragma: no cover
            # no usage
            return []
        self.usage -= 1
        active_charactor = match.player_tables[
            1 - self.position.player_idx].get_active_charactor()
        return [MakeDamageAction(
            source_player_idx = self.position.player_idx,
            target_player_idx = 1 - self.position.player_idx,
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.DAMAGE,
                    target_position = active_charactor.position,
                    damage = 2,
                    damage_elemental_type = DamageElementalType.CRYO,
                    cost = Cost()
                )
            ]
        )]

    def event_handler_SWITCH_CHARACTOR(
        self, event: SwitchCharactorEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        If self switch charactor, perform attack
        """
        if event.action.player_idx != self.position.player_idx:
            # not self switch charactor
            return []
        return self._attack(match)

    def event_handler_CHOOSE_CHARACTOR(
        self, event: ChooseCharactorEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        If self choose charactor (when ally defeated), perform attack
        """
        if event.action.player_idx != self.position.player_idx:
            # not self switch charactor
            return []
        return self._attack(match)


CryoTeamStatus = Icicle | Icicle
