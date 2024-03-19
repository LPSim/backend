from typing import Any, Dict, List, Literal
from lpsim.server.action import (
    Actions,
    CreateDiceAction,
    DrawCardAction,
    RemoveObjectAction,
)
from lpsim.server.card.support.base import UsageWithRoundRestrictionSupportBase
from lpsim.server.card.support.items import ItemBase
from lpsim.server.consts import DieColor, IconType, PlayerActionLabels
from lpsim.server.event import ActionEndEventArguments, RoundPrepareEventArguments
from lpsim.server.match import Match
from lpsim.server.struct import Cost
from lpsim.utils.class_registry import register_class
from lpsim.utils.desc_registry import DescDictType


class Lumenstonedjuvant_4_5(ItemBase, UsageWithRoundRestrictionSupportBase):
    name: Literal["Lumenstone Adjuvant"] = "Lumenstone Adjuvant"
    version: Literal["4.5"] = "4.5"
    cost: Cost = Cost(same_dice_number=2)
    max_usage_one_round: int = 1
    usage: int = 3
    counter: int = 0
    icon_type: IconType = IconType.COUNTER

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        self.counter = 0
        return super().event_handler_ROUND_PREPARE(event, match)

    def event_handler_ACTION_END(
        self, event: ActionEndEventArguments, match: Match
    ) -> List[CreateDiceAction | DrawCardAction | RemoveObjectAction]:
        """
        When used 3 cards, create 1 omni die and draw one card.
        """
        if not self.has_usage():
            return []
        if self.position.not_satisfy(
            "source area=support and both player=same id=diff", event.action.position
        ):
            return []
        if event.action.action_label & PlayerActionLabels.CARD != 0:
            # is card action
            self.counter += 1
        if self.counter < 3:
            return []
        self.use()
        return [
            CreateDiceAction(
                player_idx=self.position.player_idx,
                number=1,
                color=DieColor.OMNI,
            ),
            DrawCardAction(
                player_idx=self.position.player_idx,
                number=1,
                draw_if_filtered_not_enough=True,
            ),
        ] + self.check_should_remove()


desc: Dict[str, DescDictType] = {
    "SUPPORT/Lumenstone Adjuvant": {
        "names": {"en-US": "Lumenstone Adjuvant", "zh-CN": "流明石触媒"},
        "descs": {
            "4.5": {
                "en-US": "After you play an Action Card: If, while this card is on the field, you have already played 3 Action Cards this Round, draw 1 card and create 1 Omni Die. (Once per Round)\nUsage(s): 3",  # noqa: E501
                "zh-CN": "我方打出行动牌后：如果此牌在场期间本回合中我方已打出3张行动牌，则抓1张牌并生成1个万能元素骰。（每回合1次）\n可用次数：3",  # noqa: E501
            }
        },
        "image_path": "cardface/Assist_Prop_Liumingshi.png",  # noqa: E501
        "id": 323007,
    },
}


register_class(Lumenstonedjuvant_4_5, desc)
