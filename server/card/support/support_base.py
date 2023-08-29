from typing import Literal, List, Any
from ...object_base import CardBase
from ...consts import ObjectType, ObjectPositionType, DiceCostLabels
from ...struct import Cost
from ...action import Actions, RemoveObjectAction, MoveObjectAction
from ...struct import ObjectPosition, CardActionTarget


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
    cost: Cost
    cost_label: int = DiceCostLabels.CARD.value
    usage: int

    def check_remove_triggered(self) -> List[Actions]:
        """
        Check if the support should be removed, if it is not in support area, 
        return empty list.
        when usage has changed, call this function to check if the support
        should be removed.
        """
        raise NotImplementedError('Not tested part')
        if self.position.area != ObjectPositionType.SUPPORT:
            return []
        if self.usage <= 0:
            return [RemoveObjectAction(
                object_position = self.position,
                object_id = self.id,
            )]
        return []

    def is_valid(self, match: Any) -> bool:
        """
        If it is not in hand, cannot use.
        """
        return self.position.area == ObjectPositionType.HAND

    def get_targets(self, match: Any) -> List[CardActionTarget]:
        max_support_number = match.config.max_support_number
        supports = (
            match.player_tables[self.position.player_id].supports
        )
        assert max_support_number >= len(supports)
        if len(supports) == max_support_number:
            # choose one support to remove
            ret: List[CardActionTarget] = []
            for support in supports:
                ret.append(CardActionTarget(
                    target_position = support.position.copy(deep = True),
                    target_id = support.id,
                ))
            return ret
        return []

    def get_actions(
        self, target: CardActionTarget | None, match: Any
    ) -> List[RemoveObjectAction | MoveObjectAction]:
        """
        Act the support. will place it into support area.
        """
        ret: List[RemoveObjectAction | MoveObjectAction] = []
        max_support_number = match.config.max_support_number
        supports = (
            match.player_tables[self.position.player_id].supports
        )
        assert max_support_number >= len(supports)
        if len(supports) == max_support_number:
            assert target is not None
            ret.append(RemoveObjectAction(
                object_position = target.target_position,
                object_id = target.target_id,
            ))
        ret.append(MoveObjectAction(
            object_position = self.position,
            object_id = self.id,
            target_position = ObjectPosition(
                player_id = self.position.player_id,
                area = ObjectPositionType.SUPPORT,
            ),
        ))
        return ret
