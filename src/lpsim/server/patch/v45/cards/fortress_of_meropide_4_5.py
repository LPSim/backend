from typing import Dict, List, Literal

from pydantic import PrivateAttr
from lpsim.server.action import Actions, CreateObjectAction, RemoveObjectAction
from lpsim.server.card.support.locations import LocationBase
from lpsim.server.consts import DamageType, IconType, ObjectPositionType, ObjectType
from lpsim.server.event import (
    ReceiveDamageEventArguments,
    RoundPrepareEventArguments,
    UseCardEventArguments,
)
from lpsim.server.match import Match
from lpsim.server.modifiable_values import UseCardValue
from lpsim.server.status.team_status.base import RoundTeamStatus
from lpsim.server.struct import Cost, ObjectPosition
from lpsim.utils.class_registry import register_class
from lpsim.utils.desc_registry import DescDictType


class FortressOfMeropideStatus_4_5(RoundTeamStatus):
    name: Literal["Fortress of Meropide"] = "Fortress of Meropide"
    version: Literal["4.5"] = "4.5"
    usage: int = 1
    max_usage: int = 1
    icon_type: IconType = IconType.DEBUFF

    def event_handler_USE_CARD(
        self, event: UseCardEventArguments, match: Match
    ) -> List[RemoveObjectAction]:
        """
        check should remove
        """
        return self.check_should_remove()

    def value_modifier_USE_CARD(
        self, value: UseCardValue, match: Match, mode: Literal["TEST", "REAL"]
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
            assert mode == "REAL"
            if value.use_card:  # pragma: no branch
                value.use_card = False
                self.usage -= 1
        return value


class FortressOfMeropide_4_5(LocationBase):
    name: Literal["Fortress of Meropide"] = "Fortress of Meropide"
    version: Literal["4.5"] = "4.5"
    cost: Cost = Cost(same_dice_number=1)
    usage: int = 0
    _max_usage: int = PrivateAttr(4)
    icon_type: IconType = IconType.COUNTER

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Match
    ) -> List[Actions]:
        """
        When self active receive damage or heal, get 1 counter
        """
        if event.final_damage.damage_type not in [DamageType.DAMAGE, DamageType.HEAL]:
            return []
        if self.position.not_satisfy(
            "both player=same and source area=support and target active=true",
            target=event.final_damage.target_position,
            match=match,
        ):
            return []
        self.usage = min(self._max_usage, self.usage + 1)
        return []

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Match
    ) -> List[CreateObjectAction]:
        """
        When usage reach max, and status not exist, create status
        """
        if self.usage < self._max_usage:
            return []
        target = self.query_one(match, f'opponent team_status "name={self.name}"')
        if target is not None:
            # status already exist
            return []
        self.usage = 0
        return [
            CreateObjectAction(
                object_name=self.name,
                object_position=ObjectPosition(
                    player_idx=1 - self.position.player_idx,
                    area=ObjectPositionType.TEAM_STATUS,
                    id=0,
                ),
                object_arguments={},
            )
        ]


desc: Dict[str, DescDictType] = {
    "TEAM_STATUS/Fortress of Meropide": {
        "names": {"en-US": "Fortress of Meropide", "zh-CN": "梅洛彼得堡"},
        "descs": {
            "4.5": {
                "en-US": "1 Event Card played by you this Round will have no effect.",
                "zh-CN": "本回合中我方打出的1张事件牌无效",
            }
        },
    },
    "SUPPORT/Fortress of Meropide": {
        "names": {"en-US": "Fortress of Meropide", "zh-CN": "梅洛彼得堡"},
        "descs": {
            "4.5": {
                "en-US": 'When your active character takes DMG or is healed: This card gains 1 "Prohibition" point. (Maximum 4 points)\nWhen Action Phase begins: If this card has accumulated 4 "Prohibition" points, then 4 points will be consumed and 1 Strictly Prohibited will be created in your opponent\'s playing field. (1 Event Card played by your opponent this Round will have no effect.)',  # noqa: E501
                "zh-CN": "我方出战角色受到伤害或治疗后：此牌累积1点「禁令」。（最多累积到4点）\n行动阶段开始时：如果此牌已有4点「禁令」，则消耗4点，在对方场上生成严格禁令。（本回合中打出的1张事件牌无效）",  # noqa: E501
            }
        },
        "image_path": "cardface/Assist_Location_BideBao.png",  # noqa: E501
        "id": 321018,
    },
}


register_class(FortressOfMeropide_4_5 | FortressOfMeropideStatus_4_5, desc)
