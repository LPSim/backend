from typing import Dict, List, Literal

from ....action import Actions
from ....event import MoveObjectEventArguments
from ....card.support.base import UsageWithRoundRestrictionSupportBase
from ....card.support.items import ItemBase
from .....utils.class_registry import register_class
from ....match import Match
from ....modifiable_values import CostValue
from ....consts import CostLabels, IconType, ObjectPositionType
from ....struct import Cost
from .....utils.desc_registry import DescDictType


class SeedDispensary_4_3(ItemBase, UsageWithRoundRestrictionSupportBase):
    name: Literal["Seed Dispensary"]
    version: Literal["4.3"] = "4.3"
    cost: Cost = Cost()
    usage: int = 2
    max_usage_one_round: int = 1
    icon_type: Literal[IconType.TIMESTATE] = IconType.TIMESTATE

    decrease_target: int = CostLabels.SUPPORTS.value | CostLabels.EQUIPMENT.value
    decrease_threshold: int = 1

    def value_modifier_COST(
        self, value: CostValue, match: Match, mode: Literal["TEST", "REAL"]
    ) -> CostValue:
        """
        if card label match and original cost greater than threshold,
        reduce cost.
        """
        assert value.cost.original_value is not None
        if (
            self.position.area == ObjectPositionType.SUPPORT
            and value.position.player_idx == self.position.player_idx
            and value.cost.original_value.total_dice_cost <= self.decrease_threshold
            and value.cost.label & self.decrease_target != 0
            and self.has_usage()
        ):
            # area right, player right, cost label match, cost smaller than
            # threshold, and not used this round
            if value.cost.decrease_cost(value.cost.elemental_dice_color):
                if mode == "REAL":
                    self.use()
        return value

    def event_handler_MOVE_OBJECT(
        self, event: MoveObjectEventArguments, match: Match
    ) -> List[Actions]:
        if self.usage == 0:
            # if usage is zero, it run out of usage, remove it
            return list(self.check_should_remove())
        # otherwise, do parent event handler
        return super().event_handler_MOVE_OBJECT(event, match)


desc: Dict[str, DescDictType] = {
    "SUPPORT/Seed Dispensary": {
        "names": {"en-US": "Seed Dispensary", "zh-CN": "化种匣"},
        "descs": {
            "4.3": {
                "en-US": "When you play an Equipment or Support Card with an original cost of at least 1 Elemental Die: Spend 1 less Elemental Die. (Once per Round)\nUsage(s): 2",  # noqa: E501
                "zh-CN": "我方打出原本元素骰费用为1的装备或支援牌时：少花费1个元素骰。（每回合1次）\n可用次数：2",  # noqa: E501
            }
        },
        "image_path": "cardface/Assist_Prop_Seedbox.png",  # noqa: E501
        "id": 323005,
    },
}


register_class(SeedDispensary_4_3, desc)
