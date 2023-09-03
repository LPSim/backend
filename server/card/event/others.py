"""
Event cards that not belong to any other categories.
"""

from typing import Any, List, Literal, Tuple

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
    ) -> List[CreateDiceAction]:
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
    ) -> List[CreateObjectAction]:
        """
        Act the card. Create team status.
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
    ) -> List[GenerateRerollDiceRequestAction]:
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
    ) -> List[DrawCardAction]:
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


class LeaveItToMe(CardBase):
    name: Literal['Leave It to Me!']
    desc: str = (
        'The next time you perform "Switch Character": '
        'The switch will be considered a Fast Action instead of a '
        'Combat Action.'
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost()

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        """
        Act the card. Create team status.
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


class ClaxsArts(CardBase):
    name: Literal["Clax's Arts"]
    desc: str = (
        'Shift 1 Energy from at most 2 of your characters on standby to '
        'your active character.'
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(same_dice_number = 1)

    def _get_charge_source_and_targets(
            self, match: Any) -> Tuple[int, List[int]]:
        """
        Get charge source and targets.
        """
        table = match.player_tables[self.position.player_idx]
        source = table.active_charactor_idx
        assert source >= 0 and source < len(table.charactors)
        targets = []
        for idx, charactor in enumerate(table.charactors):
            if idx != source and charactor.charge > 0:
                targets.append(idx)
        if len(targets) > 2:
            targets = targets[:2]
        return source, targets

    def is_valid(self, match: Any) -> bool:
        source, targets = self._get_charge_source_and_targets(match)
        return len(targets) > 0

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[ChargeAction]:
        assert target is None
        source, targets = self._get_charge_source_and_targets(match)
        assert len(targets) > 0
        ret: List[ChargeAction] = []
        ret.append(ChargeAction(
            player_idx = self.position.player_idx,
            charactor_idx = source,
            charge = len(targets),
        ))
        for t in targets:
            ret.append(ChargeAction(
                player_idx = self.position.player_idx,
                charactor_idx = t,
                charge = -1,
            ))
        return ret


class HeavyStrike(CardBase):
    name: Literal['Heavy Strike']
    desc: str = (
        "During this round, your current active character's next "
        'Normal Attack deals +1 DMG. '
        'When this Normal Attack is a Charged Attack: Deal +1 additional DMG.'
    )
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(same_dice_number = 1)

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        """
        Act the card. Create charactor status.
        """
        assert target is None  # no targets
        active_charactor = match.player_tables[
            self.position.player_idx].get_active_charactor()
        position = active_charactor.position.set_area(
            ObjectPositionType.CHARACTOR_STATUS)
        return [CreateObjectAction(
            object_name = self.name,
            object_position = position,
            object_arguments = {}
        )]


OtherEventCards = (
    TheBestestTravelCompanion | ChangingShifts | TossUp | Strategize
    | IHaventLostYet | LeaveItToMe | ClaxsArts | HeavyStrike
)
