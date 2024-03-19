from typing import Dict, List, Literal
from lpsim.server.action import ChangeObjectUsageAction
from lpsim.server.match import Match
from lpsim.server.object_base import EventCardBase
from lpsim.server.struct import Cost, ObjectPosition
from lpsim.utils.class_registry import register_class
from lpsim.utils.desc_registry import DescDictType


class ControlledDirectionalBlast_4_5(EventCardBase):
    name: Literal["Controlled Directional Blast"] = "Controlled Directional Blast"
    version: Literal["4.5"] = "4.5"
    cost: Cost = Cost(same_dice_number=1)

    def is_valid(self, match: Match) -> bool:
        """
        can use if opponent has 4 or more support and summon and any summon exist
        """
        return (
            len(self.query(match, "opponent support and opponent summon")) >= 4
            and len(self.query(match, "both summon")) > 0
        )

    def get_targets(self, match: Match) -> List[ObjectPosition]:
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Match
    ) -> List[ChangeObjectUsageAction]:
        assert target is None
        targets = self.query(match, "both summon")
        ret: List[ChangeObjectUsageAction] = []
        for t in targets:
            ret.append(
                ChangeObjectUsageAction(object_position=t.position, change_usage=-1)
            )
        return ret


desc: Dict[str, DescDictType] = {
    "CARD/Controlled Directional Blast": {
        "names": {
            "en-US": "Controlled Directional Blast",
            "zh-CN": "可控性去危害化式定向爆破",
        },
        "descs": {
            "4.5": {
                "en-US": "Can only be played when there is a total of at least 4 cards in your opponent's Support Zone and Summons Zone: All Summons on both sides lose 1 Usage.",  # noqa: E501
                "zh-CN": "对方支援区和召唤物区的卡牌数量总和至少为4时，才能打出：双方所有召唤物的可用次数-1。",
            }
        },
        "image_path": "cardface/Event_Event_Kexueyuan.png",  # noqa: E501
        "id": 332030,
    },
}


register_class(ControlledDirectionalBlast_4_5, desc)
