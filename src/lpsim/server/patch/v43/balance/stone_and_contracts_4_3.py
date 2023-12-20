
from typing import Any, Dict, List, Literal

from .....utils.class_registry import register_class
from ....action import CreateObjectAction, DrawCardAction
from ....struct import ObjectPosition
from .....utils.desc_registry import DescDictType
from ....card.event.resonance import StoneAndContracts_3_7


class StoneAndContracts_4_3(StoneAndContracts_3_7):
    version: Literal['4.3'] = '4.3'

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction | DrawCardAction]:
        ret: List[CreateObjectAction | DrawCardAction] = []
        ret += super().get_actions(target, match)
        ret.append(DrawCardAction(
            player_idx = self.position.player_idx,
            number = 1,
            draw_if_filtered_not_enough = True
        ))
        return ret


desc: Dict[str, DescDictType] = {
    "CARD/Stone and Contracts": {
        "descs": {
            "4.3": {
                "zh-CN": "下回合行动阶段开始时：生成3点万能元素，抓一张牌。（牌组包含至少2个「璃月」角色，才能加入牌组）",  # noqa: E501
                "en-US": "When the Action Phase of the next Round begins: Create 3 Omni Element， draw a card. (You must have at least 2 Liyue characters in your deck to add this card to your deck.)"  # noqa: E501
            }
        },
    },
}


register_class(StoneAndContracts_4_3, desc)
