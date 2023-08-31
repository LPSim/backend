from typing import Literal, List, Any

from ...event import MoveObjectEventArguments
from ...object_base import CardBase
from ...consts import ObjectType, ObjectPositionType, CostLabels
from ...struct import Cost
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
    cost: Cost
    cost_label: int = CostLabels.CARD.value
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

    def play(self, match: Any) -> List[Actions]:
        """
        Triggered when the support is played from hand to support area.
        """
        return []

    def is_valid(self, match: Any) -> bool:
        """
        If it is not in hand, cannot use.
        """
        return self.position.area == ObjectPositionType.HAND

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        """
        When support field is full, should choose one target to remove.
        Otherwise, return empty.
        """
        max_support_number = match.config.max_support_number
        supports = (
            match.player_tables[self.position.player_idx].supports
        )
        assert max_support_number >= len(supports)
        if len(supports) == max_support_number:
            # choose one support to remove
            ret: List[ObjectPosition] = []
            for support in supports:
                ret.append(support.position.copy(deep = True))
            return ret
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[RemoveObjectAction | MoveObjectAction]:
        """
        Act the support. will place it into support area.
        """
        ret: List[RemoveObjectAction | MoveObjectAction] = []
        max_support_number = match.config.max_support_number
        supports = (
            match.player_tables[self.position.player_idx].supports
        )
        assert max_support_number >= len(supports)
        if len(supports) == max_support_number:
            assert target is not None
            ret.append(RemoveObjectAction(
                object_position = target
            ))
        ret.append(MoveObjectAction(
            object_position = self.position,
            target_position = ObjectPosition(
                player_idx = self.position.player_idx,
                area = ObjectPositionType.SUPPORT,
                id = self.position.id
            ),
        ))
        return ret

    def event_handler_MOVE_OBJECT(
        self, event: MoveObjectEventArguments, match: Any
    ) -> list[Actions]:
        """
        When this support is moved from hand to support, it is considered
        as played, and will call `self.play`.
        """
        if (
            event.action.object_position.id == self.id
            and event.action.object_position.area == ObjectPositionType.HAND
            and event.action.target_position.area 
            == ObjectPositionType.SUPPORT
        ):
            # this artifact equipped from hand to charactor
            return self.play(match)
        return []