"""
Event cards that not belong to any other categories.
"""

from typing import Any, List, Literal

from ...consts import DieColor

from ...object_base import CardBase
from ...action import CreateDiceAction, DrawCardAction
from ...struct import Cost, CardActionTarget


class Strategize(CardBase):
    name: Literal['Strategize']
    desc: str = '''Draw 2 cards.'''
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(
        same_dice_number = 1
    )

    def get_targets(self, match: Any) -> List[CardActionTarget]:
        # no targets
        return []

    def get_actions(
        self, target: CardActionTarget | None, match: Any
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


class TheBestestTravelCompanion(CardBase):
    name: Literal['The Bestest Travel Companion!']
    desc: str = '''Convert the Elemental Dice spent to Omni Element x2.'''
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(
        any_dice_number = 2
    )

    def get_targets(self, match: Any) -> List[CardActionTarget]:
        # no targets
        return []

    def get_actions(
        self, target: CardActionTarget | None, match: Any
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


OtherEventCards = Strategize | TheBestestTravelCompanion
