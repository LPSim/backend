

from typing import Any, Literal, List

from ...consts import CostLabels

from ...action import Actions, RemoveObjectAction

from ...event import (
    CharactorDefeatedEventArguments, CombatActionEventArguments
)

from ...modifiable_values import CombatActionValue, CostValue
from .base import RoundTeamStatus, UsageTeamStatus


class ChangingShifts(UsageTeamStatus):
    name: Literal['Changing Shifts'] = 'Changing Shifts'
    desc: str = (
        'The next time you perform "Switch Character": '
        'Spend 1 less Elemental Die.'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1

    def value_modifier_COST(
        self, value: CostValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> CostValue:
        assert self.usage > 0
        if not self.position.check_position_valid(
            value.position, match, player_idx_same = True,
        ):
            # not self switch charactor, do nothing
            return value
        if not (value.cost.label & CostLabels.SWITCH_CHARACTOR.value):
            # not switch charactor, do nothing
            return value
        if value.cost.any_dice_number <= 0:
            # no need dice, do nothing
            raise NotImplementedError('Not tested part')
            return value
        # self switch charactor, reduce cost by 1
        value.cost.any_dice_number -= 1
        if mode == 'REAL':
            self.usage -= 1
        return value

    def event_handler_SWITCH_CHARACTOR(
        self, event: CombatActionEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        """
        When switch charactor end, check whether to remove.
        """
        return self.check_remove_triggered()


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


EventCardTeamStatus = WindAndFreedom | ChangingShifts
