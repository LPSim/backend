"""
Event cards that not belong to any other categories.
"""

from typing import Any, List, Literal

from ...object_base import CardBase
from ...action import ActionBase, DrawCardAction
from ...struct import DiceCost, CardActionTarget


class Strategize(CardBase):
    name: Literal['Strategize']
    version: Literal['3.3'] = '3.3'
    cost: DiceCost = DiceCost(
        same_dice_number = 1
    )

    def get_targets(self, match: Any) -> List[CardActionTarget]:
        # no targets
        return []

    def get_actions(
        self, target: CardActionTarget | None, match: Any
    ) -> list[ActionBase]:
        """
        Act the card. Draw two cards.
        """
        assert target is None  # no targets
        return [DrawCardAction(player_id = self.position.player_id, 
                               number = 2)]
