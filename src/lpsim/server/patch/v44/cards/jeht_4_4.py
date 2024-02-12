from typing import Dict, List, Literal
from pydantic import PrivateAttr

from ....object_base import CreateSystemEventHandlerObject
from ....event_handler import SystemEventHandlerBase
from ....match import Match
from ....action import ChangeObjectUsageAction, CreateDiceAction, RemoveObjectAction
from ....event import (
    MoveObjectEventArguments,
    RemoveObjectEventArguments,
    SkillEndEventArguments,
)
from ....consts import DieColor, IconType, ObjectPositionType, SkillType
from ....card.support.companions import CompanionBase
from ....struct import Cost
from .....utils.class_registry import register_class
from .....utils.desc_registry import DescDictType


class JehtEventHandler_4_4(SystemEventHandlerBase):
    """
    It will be generated when Jeht in deck, and record disappeared support card numbers
    for both player, and when Jeht is played into area or any card is removed from
    support area, it will update its counter and also update all existing Jeht usage.
    """

    name: Literal["Jeht"] = "Jeht"
    version: Literal["4.4"] = "4.4"
    counters: List[int] = [0, 0]
    _max_usage: int = PrivateAttr(6)

    def _update_jedt_usage(self, match: Match) -> List[ChangeObjectUsageAction]:
        """
        check all jeht, if their usage not same as self, update it.
        """
        actions: List[ChangeObjectUsageAction] = []
        for counter, table in zip(self.counters, match.player_tables):
            for support in table.supports:
                if support.name == self.name and support.usage != counter:
                    actions.append(
                        ChangeObjectUsageAction(
                            object_position=support.position,
                            change_usage=counter - support.usage,
                        )
                    )
        return actions

    def event_handler_MOVE_OBJECT(
        self, event: MoveObjectEventArguments, match: Match
    ) -> List[ChangeObjectUsageAction]:
        if event.object_name != self.name:
            # not Jeht
            return []
        return self._update_jedt_usage(match)

    def event_handler_REMOVE_OBJECT(
        self, event: RemoveObjectEventArguments, match: Match
    ) -> List[ChangeObjectUsageAction]:
        if event.action.object_position.area != ObjectPositionType.SUPPORT:
            # not moved from support zone
            return []
        # add one usage
        pidx = event.action.object_position.player_idx
        self.counters[pidx] = min(self.counters[pidx] + 1, self._max_usage)
        return self._update_jedt_usage(match)


class Jeht_4_4(CreateSystemEventHandlerObject, CompanionBase):
    name: Literal["Jeht"]
    version: Literal["4.4"] = "4.4"
    usage: int = 0
    _max_usage: int = PrivateAttr(6)
    icon_type: Literal[IconType.TIMESTATE] = IconType.TIMESTATE
    cost: Cost = Cost(any_dice_number=2)

    handler_name: Literal["Jeht"] = "Jeht"

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Match
    ) -> List[CreateDiceAction | RemoveObjectAction]:
        if not self.position.check_position_valid(
            event.action.position,
            match,
            player_idx_same=True,
            target_area=ObjectPositionType.SKILL,
        ):
            # not self use skill
            return []
        if self.usage < 5:
            # not enough usage
            return []
        if event.action.skill_type != SkillType.ELEMENTAL_BURST:
            # not use elemental burst
            return []
        # discard self and create dice
        return [
            CreateDiceAction(
                player_idx=self.position.player_idx,
                number=self.usage - 2,
                color=DieColor.OMNI,
            ),
            RemoveObjectAction(object_position=self.position),
        ]


desc: Dict[str, DescDictType] = {
    "SUPPORT/Jeht": {
        "names": {"en-US": "Jeht", "zh-CN": "婕德"},
        "descs": {
            "4.4": {
                "en-US": "This card will record the number of cards discarded from your Support Zone during this match as Sophistication points. (Max 6 points)\nAfter your characters use an Elemental Burst: If this card has recorded at least 5 Sophistication points, discard this card and generate Omni Element equal to the number of Sophistication points minus 2.",  # noqa: E501
                "zh-CN": "此牌会记录本场对局中我方支援区弃置卡牌的数量，称为「阅历」。（最多6点）\n我方角色使用「元素爆发」后：如果「阅历」至少为5，则弃置此牌，生成「阅历」-2数量的万能元素。",  # noqa: E501
            }
        },
        "image_path": "cardface/Assist_NPC_Jeht.png",  # noqa: E501
        "id": 322022,
    },
    "SYSTEM/Jeht": {
        "names": {"en-US": "Jeht", "zh-CN": "婕德"},
        "descs": {"4.4": {}},
    },
}


register_class(Jeht_4_4 | JehtEventHandler_4_4, desc)
