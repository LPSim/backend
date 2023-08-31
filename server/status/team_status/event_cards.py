

from typing import Any, Literal, List

from ...action import Actions, RemoveObjectAction

from ...event import (
    CharactorDefeatedEventArguments, CombatActionEventArguments
)

from ...modifiable_values import CombatActionValue
from .base import RoundTeamStatus


class WindAndFreedom(RoundTeamStatus):
    name: Literal['Wind and Freedom'] = 'Wind and Freedom'
    desc: str = (
        'In this Round, when an opposing character is defeated during your '
        'Action, you can continue to act again when that Action ends. '
        'Usage(s): 1 '
    )
    version: Literal['3.7'] = '3.7'
    usage: int = 1
    max_usage: int = 1
    activated: bool = False

    def event_handler_CHARACTOR_DEFEATED(
        self, event: CharactorDefeatedEventArguments, match: Any
    ) -> List[Actions]:
        """
        When an enemy charactor is defeated, mark activated.
        """
        if (self.position.player_idx != event.action.player_idx):
            # enemy defeated, mark activated.
            self.activated = True
        return []

    def value_modifier_COMBAT_ACTION(
        self, value: CombatActionValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> CombatActionValue:
        """
        When enemy charactor defeated, 
        """
        if not self.activated:
            # not activated, do nothing
            return value
        assert self.usage > 0
        assert self.position.check_position_valid(
            value.position, match, player_idx_same = True,
        )
        # combat action end from self, if combat action, change to quick.
        if value.do_combat_action:
            value.do_combat_action = False
            self.usage -= 1
        else:
            # Mona + Kaeya may trigger
            raise NotImplementedError('Not tested part')
        return value

    def event_handler_COMBAT_ACTION(
        self, event: CombatActionEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        """
        When combat action end, check whether to remove.
        """
        return self.check_should_remove()


EventCardTeamStatus = WindAndFreedom | WindAndFreedom
