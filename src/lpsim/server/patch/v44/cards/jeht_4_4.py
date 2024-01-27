"""
TODO need a global counter hook
"""
from typing import Dict, List, Literal

from pydantic import PrivateAttr
from ....match import Match
from ....action import Actions, CreateDiceAction, RemoveObjectAction
from ....event import (
    RemoveObjectEventArguments, SkillEndEventArguments
)
from ....consts import (
    DieColor, IconType, ObjectPositionType, SkillType
)
from ....card.support.companions import CompanionBase
from ....struct import Cost
from .....utils.class_registry import register_class
from .....utils.desc_registry import DescDictType


class Jeht_4_4(CompanionBase):
    name: Literal['Jeht']
    version: Literal['4.4'] = '4.4'
    usage: int = 0
    _max_usage: int = PrivateAttr(6)
    icon_type: Literal[IconType.TIMESTATE] = IconType.TIMESTATE
    cost: Cost = Cost(any_dice_number = 2)

    def event_handler_REMOVE_OBJECT(
        self, event: RemoveObjectEventArguments, match: Match
    ) -> List[Actions]:
        if not self.position.check_position_valid(
            event.action.object_position, match, player_idx_same = True,
            target_area = ObjectPositionType.SUPPORT,
            source_area = ObjectPositionType.SUPPORT
        ):
            # not self or source or target not in support zone
            return []
        # add one usage
        self.usage = min(self.usage + 1, self._max_usage)
        return []

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Match
    ) -> List[CreateDiceAction | RemoveObjectAction]:
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            target_area = ObjectPositionType.SKILL
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
                player_idx = self.position.player_idx,
                number = self.usage - 2,
                color = DieColor.OMNI
            ),
            RemoveObjectAction(
                object_position = self.position
            )
        ]


desc: Dict[str, DescDictType] = {
    "SUPPORT/Jeht": {
        "names": {
            "en-US": "Jeht",
            "zh-CN": "婕德"
        },
        "descs": {
            "4.4": {
                "en-US": "This card will record the number of cards discarded from your Support Zone during this match as Sophistication points. (Max 6 points)\nAfter your characters use an Elemental Burst: If this card has recorded at least 5 Sophistication points, discard this card and generate Omni Element equal to the number of Sophistication points minus 2.",  # noqa: E501
                "zh-CN": "此牌会记录本场对局中我方支援区弃置卡牌的数量，称为「阅历」。（最多6点）\n我方角色使用「元素爆发」后：如果「阅历」至少为5，则弃置此牌，生成「阅历」-2数量的万能元素。"  # noqa: E501
            }
        },
        "image_path": "https://api.ambr.top/assets/UI/gcg/UI_Gcg_CardFace_Assist_NPC_Jeht.png",  # noqa: E501
        "id": 322022
    },
}


register_class(Jeht_4_4, desc)
