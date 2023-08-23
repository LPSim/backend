"""
Event cards that not belong to any other categories.
"""

from typing import Literal
from ...object_base import CardBase
from ...action import ActionBase, DrawCardAction
from ...modifiable_values import DiceCostValue


class Strategize(CardBase):
    name: Literal['Strategize']
    version: Literal['3.3'] = '3.3'
    cost: DiceCostValue = DiceCostValue(
        same_dice_number = 1
    )

    def get_actions(self) -> list[ActionBase]:
        """
        Act the card. Draw two cards.
        """
        return [DrawCardAction(player_id = self.position.player_id, 
                               number = 2)]
