from typing import Dict, List, Literal

from .....utils.class_registry import register_class
from ....action import DrawCardAction, RemoveObjectAction
from ....match import Match
from ....event import RoundEndEventArguments
from ....consts import IconType
from ....struct import Cost
from ....card.support.locations import LocationBase
from .....utils.desc_registry import DescDictType


class WeepingWillowOfTheLake_4_3(LocationBase):
    name: Literal['Weeping Willow of the Lake']
    version: Literal['4.3'] = '4.3'
    cost: Cost = Cost(same_dice_number = 1)
    usage: int = 2
    icon_type: Literal[IconType.TIMESTATE] = IconType.TIMESTATE

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Match
    ) -> List[DrawCardAction | RemoveObjectAction]:
        """
        When in round end, if hand size less than 2, draw 2 cards, and check 
        if should remove.
        """
        if self.position.area != 'SUPPORT':
            # not in support area, do nothing
            return []
        if len(match.player_tables[self.position.player_idx].hands) > 2:
            # hand size more than 2, do nothing
            return []
        self.usage -= 1
        return [
            DrawCardAction(
                player_idx = self.position.player_idx,
                number = 2,
                draw_if_filtered_not_enough = True
            ),
        ] + self.check_should_remove()


desc: Dict[str, DescDictType] = {
    "SUPPORT/Weeping Willow of the Lake": {
        "names": {
            "en-US": "Weeping Willow of the Lake",
            "zh-CN": "湖中垂柳"
        },
        "descs": {
            "4.3": {
                "en-US": "End Phase: If your Hand has no more than 2 cards, draw 2 cards.\nUsage(s): 2",  # noqa: E501
                "zh-CN": "结束阶段：如果我方手牌数量不多于2，则抓2张牌。\n可用次数：2"  # noqa: E501
            }
        },
        "image_path": "cardface/Assist_Location_Chuiliu.png",  # noqa: E501
        "id": 321016
    },
}


register_class(WeepingWillowOfTheLake_4_3, desc)
