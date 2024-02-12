from typing import Dict, List, Literal

from .....utils.class_registry import register_class

from .....utils.desc_registry import DescDictType
from ....action import ConsumeArcaneLegendAction, DrawCardAction
from ....card.event.arcane_legend import ArcaneLegendBase
from ....match import Match
from ....struct import Cost, ObjectPosition


class InEveryHouseAStove_4_4(ArcaneLegendBase):
    name: Literal["In Every House a Stove"]
    version: Literal["4.4"] = "4.4"
    cost: Cost = Cost(arcane_legend=True)

    def get_targets(self, match: Match) -> List[ObjectPosition]:
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Match
    ) -> List[ConsumeArcaneLegendAction | DrawCardAction]:
        """
        Draw cards.
        """
        assert target is None
        return super().get_actions(target, match) + [
            DrawCardAction(
                player_idx=self.position.player_idx,
                number=min(match.round_number - 1, 4),
                draw_if_filtered_not_enough=True,
            )
        ]


desc: Dict[str, DescDictType] = {
    "ARCANE/In Every House a Stove": {
        "descs": {
            "4.4": {
                "zh-CN": "我方抓相当于当前的回合数减1的牌。（最多抓4张）（整局游戏只能打出一张「秘传」卡牌；这张牌一定在你的起始手牌中）",  # noqa: E501
                "en-US": 'Draw a number of cards equal to the current Round number minus 1. (Up to 4 cards can be drawn in this way) (Only one "Arcane Legend" card can be played for the entire game. This card will be in your starting hand.)',  # noqa: E501
            }
        },
    },
}


register_class(InEveryHouseAStove_4_4, desc)
