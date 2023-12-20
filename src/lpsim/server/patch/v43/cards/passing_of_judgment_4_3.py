from re import Match
from typing import Dict, List, Literal

from .....utils.class_registry import register_class
from ....modifiable_values import UseCardValue
from ....event import RoundPrepareEventArguments, UseCardEventArguments
from ....status.team_status.base import UsageTeamStatus
from ....consts import IconType, ObjectPositionType, ObjectType
from ....action import (
    ConsumeArcaneLegendAction, CreateObjectAction, RemoveObjectAction
)
from ....struct import Cost, ObjectPosition
from ....card.event.arcane_legend import ArcaneLegendBase
from .....utils.desc_registry import DescDictType


class PassingOfJudgmentStatus_4_3(UsageTeamStatus):
    name: Literal['Passing of Judgment']
    version: Literal['4.3'] = '4.3'
    usage: int = 3
    max_usage: int = 3
    icon_type: IconType = IconType.DEBUFF

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Match
    ) -> List[RemoveObjectAction]:
        """
        In prepare, remove self
        """
        self.usage = 0
        return self.check_should_remove()

    def event_handler_USE_CARD(
        self, event: UseCardEventArguments, match: Match
    ) -> List[RemoveObjectAction]:
        """
        check should remove
        """
        return self.check_should_remove()

    def value_modifier_USE_CARD(
        self, value: UseCardValue, match: Match, mode: Literal['TEST', 'REAL']
    ) -> UseCardValue:
        """
        When self use a event card, make using card failed.
        """
        if value.position.player_idx != self.position.player_idx:
            # not self, return
            return value
        if value.card.type in [ObjectType.CARD, ObjectType.ARCANE]:
            # is target card type
            assert self.usage > 0
            assert mode == 'REAL'
            if value.use_card:  # pragma: no branch
                value.use_card = False
                self.usage -= 1
        return value


class PassingOfJudgment_4_3(ArcaneLegendBase):
    """
    TODO: will it block talent+event card, e.g. Electro Hypostasis talent?
    """
    name: Literal['Passing of Judgment']
    version: Literal['4.3'] = '4.3'
    cost: Cost = Cost(
        same_dice_number = 1,
        arcane_legend = True
    )

    def get_targets(self, match: Match) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Match
    ) -> List[ConsumeArcaneLegendAction | CreateObjectAction]:
        return super().get_actions(target, match) + [
            CreateObjectAction(
                object_position = ObjectPosition(
                    player_idx = 1 - self.position.player_idx,
                    area = ObjectPositionType.TEAM_STATUS,
                    id = -1
                ),
                object_name = self.name,
                object_arguments = {}
            )
        ]


desc: Dict[str, DescDictType] = {
    "TEAM_STATUS/Passing of Judgment": {
        "names": {
            "en-US": "Passing of Judgment",
            "zh-CN": "裁定之时"
        },
        "descs": {
            "4.3": {
                "en-US": "The next 3 Event Cards played by you in this Round will take no effect.",  # noqa: E501
                "zh-CN": "本回合中，你接下来打出的3张事件牌无效。"
            }
        },
    },
    "ARCANE/Passing of Judgment": {
        "names": {
            "en-US": "Passing of Judgment",
            "zh-CN": "裁定之时"
        },
        "descs": {
            "4.3": {
                "en-US": "3 Event Cards played by your opponent in this Round will take no effect.\n(Only one \"Arcane Legend\" card can be played per match. This card will be in your starting hand.)",  # noqa: E501
                "zh-CN": "本回合中，对方牌手打出的3张事件牌无效。\n（整局游戏只能打出一张「秘传」卡牌；这张牌一定在你的起始手牌中）"  # noqa: E501
            }
        },
        "image_path": "cardface/Event_Event_Xuanpanyouzui.png",  # noqa: E501
        "id": 330006
    },
}


register_class(PassingOfJudgment_4_3 | PassingOfJudgmentStatus_4_3, desc)
