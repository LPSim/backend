

from typing import Any, List, Literal
from server.action import CreateObjectAction
from ...consts import ObjectPositionType

from server.struct import ObjectPosition
from ...object_base import CardBase
from ...struct import Cost


class ElementalResonanceCardBase(CardBase):
    ...  # pragma: no cover


class NationResonanceCardBase(CardBase):
    pass


class WindAndFreedom(NationResonanceCardBase):
    name: Literal['Wind and Freedom']
    desc: str = (
        'In this Round, when an opposing character is defeated during your '
        'Action, you can continue to act again when that Action ends. '
        'Usage(s): 1 '
        '(You must have at least 2 Mondstadt characters in your deck to add '
        'this card to your deck.)'
    )
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(same_dice_number = 1)

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        """
        Create Wind and Freedom team status.
        """
        assert target is None
        return [CreateObjectAction(
            object_name = 'Wind and Freedom',
            object_position = ObjectPosition(
                player_idx = self.position.player_idx,
                area = ObjectPositionType.TEAM_STATUS,
                id = -1,
            ),
            object_arguments = {},
        )]


NationResonanceCards = WindAndFreedom | WindAndFreedom
