from typing import Dict, List, Literal
from lpsim.server.action import CreateDiceAction, RemoveObjectAction

from lpsim.server.card.support.locations import JadeChamber_4_0
from lpsim.server.consts import DieColor, ObjectPositionType
from lpsim.server.event import RoundPrepareEventArguments
from lpsim.server.match import Match
from lpsim.utils.class_registry import register_class
from lpsim.utils.desc_registry import DescDictType


class JadeChamber_4_5(JadeChamber_4_0):
    version: Literal["4.5"] = "4.5"

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Match
    ) -> List[CreateDiceAction | RemoveObjectAction]:
        """
        When hand number less than 3, create 1 omni die and remove self.
        """
        if (
            self.position.area != ObjectPositionType.SUPPORT
            or len(match.player_tables[self.position.player_idx].hands) > 3
        ):
            return []
        return [
            CreateDiceAction(
                player_idx=self.position.player_idx,
                number=1,
                color=DieColor.OMNI,
            ),
            RemoveObjectAction(object_position=self.position),
        ]


desc: Dict[str, DescDictType] = {
    "SUPPORT/Jade Chamber": {
        "descs": {
            "4.5": {
                "zh-CN": "投掷阶段：2个元素骰初始总是投出我方出战角色类型的元素。\n行动阶段开始时：如果我方手牌数量不多于3，则弃置此牌，生成1个万能元素。",  # noqa: E501
                "en-US": "Roll Phase: 2 initial Elemental Dice will be of the same Elemental type as your active character.\nWhen Action Phase begins: If you have no more than 3 cards in your Hand, discard this card and create 1 Omni Element.",  # noqa: E501
            }
        },
    },
}


register_class(JadeChamber_4_5, desc)
