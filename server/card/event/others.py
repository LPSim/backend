"""
Event cards that not belong to any other categories.
"""

from typing import Literal
from server.card.card_base import CardBase
from server.action import ActionBase, DrawCardAction


class Strategize(CardBase):
    name: Literal['Strategize'] = 'Strategize'

    def act(self) -> list[ActionBase]:
        """
        Act the card. Draw two cards.
        """
        return [DrawCardAction(object_id = -1, player_id = -1, number = 2)]
