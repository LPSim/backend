
from typing import Any, Dict, List, Literal

from ....status.team_status.event_cards import (
    StoneAndContracts_3_7 as StoneAndContractsStatus_3_7
)

from .....utils.class_registry import register_class
from ....action import CreateDiceAction, DrawCardAction, RemoveObjectAction
from .....utils.desc_registry import DescDictType
from ....card.event.resonance import StoneAndContracts_3_7


class StoneAndContractsStatus_4_3(StoneAndContractsStatus_3_7):
    version: Literal['4.3'] = '4.3'

    def event_handler_ROUND_PREPARE(
        self, event: Any, match: Any
    ) -> List[CreateDiceAction | RemoveObjectAction | DrawCardAction]:
        """
        When round prepare, create 3 omni element and remove self.
        """
        return super().event_handler_ROUND_PREPARE(event, match) + [
            DrawCardAction(
                player_idx = self.position.player_idx,
                number = 1,
                draw_if_filtered_not_enough = True
            )
        ]


class StoneAndContracts_4_3(StoneAndContracts_3_7):
    version: Literal['4.3'] = '4.3'


desc: Dict[str, DescDictType] = {
    "TEAM_STATUS/Stone and Contracts": {
        "descs": {
            "4.3": {
                "zh-CN": "下回合行动阶段开始时：生成3点万能元素，抓一张牌。",
                "en-US": "When the Action Phase of the next Round begins: Create 3 Omni Element, draw a card."  # noqa: E501
            }
        },
    },
    "CARD/Stone and Contracts": {
        "descs": {
            "4.3": {
                "zh-CN": "下回合行动阶段开始时：生成3点万能元素，抓一张牌。（牌组包含至少2个「璃月」角色，才能加入牌组）",  # noqa: E501
                "en-US": "When the Action Phase of the next Round begins: Create 3 Omni Element, draw a card. (You must have at least 2 Liyue characters in your deck to add this card to your deck.)"  # noqa: E501
            }
        },
    },
}


register_class(StoneAndContractsStatus_4_3 | StoneAndContracts_4_3, desc)
