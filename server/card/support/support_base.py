from typing import Literal, List
from ...object_base import CardBase
from ...consts import ObjectType, ObjectPositionType, DiceCostLabels
from ...modifiable_values import DiceCostValue
from ...action import Actions, RemoveObjectAction, MoveObjectAction
from ...struct import ObjectPosition


class SupportBase(CardBase):
    """
    Supports are cards that can be played on the table. Based on its position,
    it will have different actions. When in hand, it performs like a event
    card that have costs, is_valid, and get_actions. When on the table, its
    event triggers will work and do supports.
    """
    name: str
    type: Literal[ObjectType.SUPPORT] = ObjectType.SUPPORT
    version: str
    cost: DiceCostValue
    cost_label: int = DiceCostLabels.CARD.value
    usage: int

    def check_remove_triggered(self) -> List[Actions]:
        """
        Check if the support should be removed, if it is not in support area, 
        return empty list.
        when usage has changed, call this function to check if the support
        should be removed.
        """
        if self.position.area != ObjectPositionType.SUPPORT:
            return []
        if self.usage <= 0:
            return [RemoveObjectAction(
                object_position = self.position,
                object_id = self.id,
            )]
        return []

    def act(self):
        """
        when this support card is activated from hand, this function is called
        to update the status.
        """
        raise NotImplementedError()

    def get_actions(self) -> List[MoveObjectAction]:
        """
        Act the support. will place it into support area.
        TODO: when support area number exceeded, remove one selected support.
        """
        return [MoveObjectAction(
            object_position = self.position,
            object_id = self.id,
            target_position = ObjectPosition(
                player_id = self.position.player_id,
                charactor_id = -1,
                area = ObjectPositionType.SUPPORT,
            ),
        )]
