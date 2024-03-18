from typing import Any, List, Literal
from lpsim.server.action import (
    ConsumeArcaneLegendAction,
    CreateObjectAction,
    RemoveObjectAction,
)

from lpsim.server.card.event.arcane_legend import ArcaneLegendBase
from lpsim.server.consts import IconType, ObjectPositionType
from lpsim.server.event import RoundPrepareEventArguments
from lpsim.server.match import Match
from lpsim.server.status.character_status.base import DefendCharacterStatus
from lpsim.server.struct import Cost, ObjectPosition
from lpsim.utils.class_registry import register_class
from lpsim.utils.desc_registry import DescDictType


class DayOfResistanceMomentOfShatteredDreamsStatus_4_5(DefendCharacterStatus):
    name: Literal[
        "Day of Resistance: Moment of Shattered Dreams"
    ] = "Day of Resistance: Moment of Shattered Dreams"
    version: Literal["4.5"] = "4.5"
    usage: int = 4
    max_usage: int = 4
    min_damage_to_trigger: int = 1
    max_in_one_time: int = 1
    icon_type: IconType = IconType.BARRIER

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Match
    ) -> List[RemoveObjectAction]:
        return [
            RemoveObjectAction(
                object_position=self.position,
            )
        ]


class DayOfResistanceMomentOfShatteredDreams_4_5(ArcaneLegendBase):
    name: Literal[
        "Day of Resistance: Moment of Shattered Dreams"
    ] = "Day of Resistance: Moment of Shattered Dreams"
    version: Literal["4.5"] = "4.5"
    cost: Cost = Cost(arcane_legend=True)

    def get_targets(self, match: Match) -> List[ObjectPosition]:
        target = self.query(match, "our character is_alive=True")
        target_pos = [x.position for x in target]
        return target_pos

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[ConsumeArcaneLegendAction | CreateObjectAction]:
        assert target is not None
        ret: List[ConsumeArcaneLegendAction | CreateObjectAction] = list(
            super().get_actions(target, match)
        )
        ret.append(
            CreateObjectAction(
                object_name=self.name,
                object_position=target.set_area(ObjectPositionType.CHARACTER_STATUS),
                object_arguments={},
            )
        )
        return ret


desc: dict[str, DescDictType] = {
    "CHARACTER_STATUS/Day of Resistance: Moment of Shattered Dreams": {
        "names": {
            "en-US": "Day of Resistance: Moment of Shattered Dreams",
            "zh-CN": "抗争之日·碎梦之时",
        },
        "descs": {
            "4.5": {
                "en-US": "During this Round, this character takes -1 DMG. (Max 4 times)",  # noqa: E501
                "zh-CN": "本回合中，角色受到的伤害-1。（最多生效4次）",
            }
        },
    },
    "ARCANE/Day of Resistance: Moment of Shattered Dreams": {
        "names": {
            "en-US": "Day of Resistance: Moment of Shattered Dreams",
            "zh-CN": "抗争之日·碎梦之时",
        },
        "descs": {
            "4.5": {
                "en-US": 'During this Round, your targeted character takes -1 DMG. (Max 4 times)\n(Only one "Arcane Legend" card can be played per match. This card will be in your starting hand.)',  # noqa: E501
                "zh-CN": "本回合中，目标我方角色受到的伤害-1。（最多生效4次）\n（整局游戏只能打出一张「秘传」卡牌；这张牌一定在你的起始手牌中）",  # noqa: E501
            }
        },
        "image_path": "cardface/Event_Event_Fankang.png",  # noqa: E501
        "id": 330007,
    },
}


register_class(
    DayOfResistanceMomentOfShatteredDreams_4_5
    | DayOfResistanceMomentOfShatteredDreamsStatus_4_5,
    desc,
)
