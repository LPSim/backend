from typing import Any, Dict, List, Literal
from lpsim.server.action import DrawCardAction
from lpsim.server.object_base import EventCardBase
from lpsim.server.struct import Cost, ObjectPosition
from lpsim.utils.class_registry import register_class
from lpsim.utils.desc_registry import DescDictType


class BigStrategize_3_3(EventCardBase):
    """
    Big Strategize
    """
    name: Literal['Big Strategize'] = 'Big Strategize'
    version: Literal['3.3'] = '3.3'
    cost = Cost(
        any_dice_number = 2
    )

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[DrawCardAction]:
        """
        Act the card. Draw three cards.
        """
        assert target is None  # no targets
        return [DrawCardAction(
            player_idx = self.position.player_idx, 
            number = 3,
            draw_if_filtered_not_enough = True
        )]


card_descs: Dict[str, DescDictType] = {
    'CARD/Big Strategize': {
        'names': {
            'zh-CN': '大心海',
            'en-US': 'Big Strategize',
        },
        "descs": {
            "3.3": {
                "zh-CN": "抓3张牌。",
                "en-US": "Draw 3 cards."
            }
        },
        "id": 332099,
        "image_path": "cardface/Event_Event_Yunchouweiwo.png"
    }
}


register_class(BigStrategize_3_3, card_descs)
