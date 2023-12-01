from typing import Literal, List, Any

from ....utils.class_registry import register_base_class

from ...event import MoveObjectEventArguments, RoundPrepareEventArguments
from ...object_base import CardBase
from ...consts import IconType, ObjectType, ObjectPositionType
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
    version: str
    cost: Cost
    usage: int
    type: Literal[ObjectType.SUPPORT] = ObjectType.SUPPORT
    remove_when_used: bool = False

    # icon type is used to show the icon on the summon top right. 
    icon_type: Literal[
        IconType.SHIELD, IconType.BARRIER, IconType.TIMESTATE, 
        IconType.COUNTER, IconType.NONE
    ]
    # when status icon type is not none, it will show in team status area
    status_icon_type: Literal[IconType.NONE] = IconType.NONE

    def check_should_remove(self) -> List[RemoveObjectAction]:
        """
        Check if the support should be removed.
        when usage has changed, call this function to check if the support
        should be removed.
        """
        if (
            self.position.area != ObjectPositionType.SUPPORT
        ):  # pragma: no cover
            return []
        if self.usage <= 0:
            return [RemoveObjectAction(
                object_position = self.position,
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
                ret.append(support.position)
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
    ) -> List[Actions]:
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


register_base_class(SupportBase)


class RoundEffectSupportBase(SupportBase):
    """
    Supports that has round effects. Refresh their usage when played and
    at round preparing stage.
    Instead of setting usage, set max_usage_per_round.
    """
    name: str
    version: str
    cost: Cost
    max_usage_per_round: int 

    usage: int = 0

    icon_type: Literal[IconType.NONE] = IconType.NONE

    def play(self, match: Any) -> List[Actions]:
        self.usage = self.max_usage_per_round
        return []

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        self.usage = self.max_usage_per_round
        return []


class UsageWithRoundRestrictionSupportBase(SupportBase):
    """
    Supports that restricts maximum usage per round, and also has total
    maximum usage. e.g. Liu Su has 1 usage per round and 2 total usage.
    """
    name: str
    version: str
    cost: Cost
    usage: int = 2
    usage_this_round: int = 0
    max_usage_one_round: int

    icon_type: Literal[IconType.TIMESTATE] = IconType.TIMESTATE

    def play(self, match: Any) -> List[Actions]:
        self.usage_this_round = self.max_usage_one_round
        return super().play(match)

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        self.usage_this_round = self.max_usage_one_round
        return []

    def has_usage(self) -> bool:
        return self.usage > 0 and self.usage_this_round > 0

    def use(self) -> None:
        assert self.has_usage()
        self.usage -= 1
        self.usage_this_round -= 1


class LimitedEffectSupportBase(SupportBase):
    """
    Supports that has limited effect during the game. e.g. Chef Mao in 4.1
    will draw 1 food card when triggered only once. 

    Overwrite the _limited_action function to do the limited action, and call
    do_limited_action when the condition is satisfied.
    """

    name: str
    version: str
    cost: Cost
    limited_usage: int

    def _limited_action(self, match: Any) -> List[Actions]:
        """
        return limited action.
        """
        raise NotImplementedError()

    def do_limited_action(self, match: Any) -> List[Actions]:
        """
        do the limited action when has usage and is in support area.
        """
        if (
            self.limited_usage <= 0 
            or self.position.area != ObjectPositionType.SUPPORT
        ):
            return []
        self.limited_usage -= 1
        return self._limited_action(match)
