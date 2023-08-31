"""
Event cards that not belong to any other categories.
"""

from typing import Any, List, Literal

from ...event import RoundPrepareEventArguments

from ...consts import DieColor, ObjectPositionType

from ...object_base import CardBase
from ...action import (
    Actions, CharactorDefeatedAction, ChargeAction, CreateDiceAction, 
    CreateObjectAction, DrawCardAction, GenerateRerollDiceRequestAction
)
from ...struct import Cost, ObjectPosition


class TheBestestTravelCompanion(CardBase):
    name: Literal['The Bestest Travel Companion!']
    desc: str = '''Convert the Elemental Dice spent to Omni Element x2.'''
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(
        any_dice_number = 2
    )

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> list[CreateDiceAction]:
        """
        Act the card. Convert the Elemental Dice spent to Omni Element x2.
        """
        assert target is None  # no targets
        return [CreateDiceAction(
            player_idx = self.position.player_idx,
            color = DieColor.OMNI,
            number = 2,
        )]


class ChangingShifts(CardBase):
    name: Literal['Changing Shifts']
    desc: str = (
        'The next time you perform "Switch Character": '
        'Spend 1 less Elemental Die.'
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost()

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> list[CreateObjectAction]:
        """
        Act the card. Convert the Omni Element Dice spent to Elemental Dice x2.
        """
        assert target is None  # no targets
        return [CreateObjectAction(
            object_name = self.name,
            object_position = ObjectPosition(
                player_idx = self.position.player_idx,
                area = ObjectPositionType.TEAM_STATUS,
                id = -1,
            ),
            object_arguments = {}
        )]


class TossUp(CardBase):
    name: Literal['Toss-Up']
    desc: str = '''Select any Elemental Dice to reroll. Can reroll 2 times.'''
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost()

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> list[GenerateRerollDiceRequestAction]:
        assert target is None
        return [GenerateRerollDiceRequestAction(
            player_idx = self.position.player_idx,
            reroll_times = 2,
        )]


class Strategize(CardBase):
    name: Literal['Strategize']
    desc: str = '''Draw 2 cards.'''
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(
        same_dice_number = 1
    )

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> list[DrawCardAction]:
        """
        Act the card. Draw two cards.
        """
        assert target is None  # no targets
        return [DrawCardAction(
            player_idx = self.position.player_idx, 
            number = 2,
            draw_if_filtered_not_enough = True
        )]


class IHaventLostYet(CardBase):
    name: Literal["I Haven't Lost Yet!"]
    desc: str = (
        "Only playable if one of your characters is defeated this Round: "
        "Create Omni Element x1 and your current active character gains 1 "
        "Energy. "
        "(Only one copy of I Haven't Lost Yet! can be played each round.)"
    )
    version: Literal['4.0'] = '4.0'
    cost: Cost = Cost()

    activated: bool = False

    def is_valid(self, match: Any) -> bool:
        team_status = match.player_tables[self.position.player_idx].team_status
        for status in team_status:
            if status.name == self.name:
                # activated in this round
                return False
        return self.activated

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[ChargeAction | CreateDiceAction | CreateObjectAction]:
        """
        1 omni die, 1 energy, and generate used status.
        """
        assert target is None
        return [
            CreateDiceAction(
                player_idx = self.position.player_idx,
                color = DieColor.OMNI,
                number = 1,
            ),
            ChargeAction(
                player_idx = self.position.player_idx,
                charactor_idx = match.player_tables[
                    self.position.player_idx].active_charactor_idx,
                charge = 1
            ),
            CreateObjectAction(
                object_name = self.name,
                object_position = ObjectPosition(
                    player_idx = self.position.player_idx,
                    area = ObjectPositionType.TEAM_STATUS,
                    id = -1,
                ),
                object_arguments = {}
            )
        ]

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        """
        Reset activated.
        """
        self.activated = False
        return []

    def event_handler_CHARACTOR_DEFEATED(
        self, event: CharactorDefeatedAction, match: Any
    ) -> List[Actions]:
        """
        Mark activated.
        """
        self.activated = True
        return []


OtherEventCards = (
    TheBestestTravelCompanion | ChangingShifts | TossUp | Strategize
    | IHaventLostYet
)
