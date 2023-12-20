from typing import Dict, List, Literal

from .....utils.class_registry import register_class

from ....modifiable_values import CostValue
from ....match import Match
from ....status.team_status.base import RoundTeamStatus
from ....consts import CostLabels, IconType, ObjectPositionType
from ....action import CreateObjectAction
from ....struct import Cost, ObjectPosition
from ....object_base import EventCardBase
from .....utils.desc_registry import DescDictType


class FallsAndFortuneStatus_4_3(RoundTeamStatus):
    # TODO both player have the status
    name: Literal["Falls and Fortune"] = "Falls and Fortune"
    version: Literal["4.3"] = "4.3"
    usage: int = 1
    max_usage: int = 1
    icon_type: IconType = IconType.DEBUFF

    def value_modifier_COST(
        self, value: CostValue, match: Match, mode: Literal['TEST', 'REAL'],
    ) -> CostValue:
        """
        if talent activated, increase switch cost
        """
        if value.cost.label & CostLabels.SWITCH_CHARACTOR.value != 0:
            # increase switch cost regardless of player
            value.cost.any_dice_number += 1
        return value


class FallsAndFortune_4_3(EventCardBase):
    name: Literal["Falls and Fortune"]
    version: Literal["4.3"] = "4.3"
    cost: Cost = Cost(same_dice_number = 1)

    def is_valid(self, match: Match) -> bool:
        return (
            len(match.player_tables[self.position.player_idx].dice.colors) >= 8
            and not match.player_tables[
                1 - self.position.player_idx].has_round_ended
        )

    def get_targets(self, match: Match) -> List[ObjectPosition]:
        # no target
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Match
    ) -> List[CreateObjectAction]:
        assert target is None
        return [CreateObjectAction(
            object_name = self.name,
            object_position = ObjectPosition(
                player_idx = self.position.player_idx,
                area = ObjectPositionType.TEAM_STATUS,
                id = -1
            ),
            object_arguments = {}
        )]


desc: Dict[str, DescDictType] = {
    "TEAM_STATUS/Falls and Fortune": {
        "names": {
            "en-US": "Falls and Fortune",
            "zh-CN": "坍陷与契机"
        },
        "descs": {
            "4.3": {
                "en-US": "In this Round, both sides must spend 1 extra Elemental Die to switch characters.",  # noqa: E501
                "zh-CN": "本回合中，双方牌手进行「切换角色」行动时需要额外花费1个元素骰。"  # noqa: E501
            }
        },
    },
    "CARD/Falls and Fortune": {
        "names": {
            "en-US": "Falls and Fortune",
            "zh-CN": "坍陷与契机"
        },
        "descs": {
            "4.3": {
                "en-US": "Can only be played when you have at least 8 Elemental Dice remaining and your opponent has not ended their Round: In this Round, both sides must spend 1 extra Elemental Die to switch characters.",  # noqa: E501
                "zh-CN": "我方至少剩余8个元素骰，且对方未宣布结束时，才能打出：本回合中，双方牌手进行「切换角色」行动时需要额外花费1个元素骰。"  # noqa: E501
            }
        },
        "image_path": "cardface/Event_Event_Tanta.png",  # noqa: E501
        "id": 332026
    },
}


register_class(FallsAndFortune_4_3 | FallsAndFortuneStatus_4_3, desc)
