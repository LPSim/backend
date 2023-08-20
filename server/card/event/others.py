"""
Event cards that not belong to any other categories.
"""

from typing import Literal
from ...object_base import CardBase
from server.action import ActionBase, DrawCardAction


class Strategize(CardBase):
    name: Literal['Strategize']
    version: Literal['3.3'] = '3.3'

    def act(self) -> list[ActionBase]:
        """
        Act the card. Draw two cards.
        """
        return [DrawCardAction(player_id = -1, number = 2)]
