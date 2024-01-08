from typing import Any, Dict, Literal

from .....utils.class_registry import register_class
from ....modifiable_values import CostValue
from ....consts import IconType, ObjectPositionType
from ....status.charactor_status.base import (
    RoundCharactorStatus, UsageCharactorStatus
)
from ....struct import Cost
from ....card.event.foods import AllCharactorFoodCard
from .....utils.desc_registry import DescDictType


class FishAndChipsStatus_4_3(RoundCharactorStatus, UsageCharactorStatus):
    name: Literal['Fish and Chips'] = 'Fish and Chips'
    version: Literal['4.3'] = '4.3'
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.BUFF] = IconType.BUFF

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['TEST', 'REAL']
    ) -> CostValue:
        """
        If this charactor use skill, decrease 1 cost.
        """
        if self.usage <= 0:  # pragma: no cover
            # no usage, not modify
            return value
        if not self.position.check_position_valid(
            value.position, match, player_idx_same = True,
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL,
        ):
            # not charactor use skill, not modify
            return value
        # modify
        if value.cost.decrease_cost(value.cost.elemental_dice_color):  # pragma: no branch  # noqa: E501
            # decrease success
            if mode == 'REAL':
                self.usage -= 1
        return value


class FishAndChips_4_3(AllCharactorFoodCard):
    name: Literal["Fish and Chips"]
    version: Literal["4.3"] = "4.3"
    cost: Cost = Cost(any_dice_number = 2)
    can_eat_only_if_damaged: bool = False


desc: Dict[str, DescDictType] = {
    "CARD/Fish and Chips": {
        "names": {
            "en-US": "Fish and Chips",
            "zh-CN": "炸鱼薯条"
        },
        "descs": {
            "4.3": {
                "en-US": "During this Round, all your characters will use 1 less Elemental Die when using their next Skill.\n(A character can consume at most 1 Food per Round)",  # noqa: E501
                "zh-CN": "本回合中，所有我方角色下次使用技能时少花费1个元素骰。\n（每回合每个角色最多食用1次「料理」）"  # noqa: E501
            }
        },
        "image_path": "cardface/Event_Food_Chips.png",  # noqa: E501
        "id": 333013
    },
    "CHARACTOR_STATUS/Fish and Chips": {
        "names": {
            "en-US": "Fish and Chips",
            "zh-CN": "炸鱼薯条"
        },
        "descs": {
            "4.3": {
                "en-US": "During this Round, this character will use 1 less Elemental Die when using their next Skill.",  # noqa: E501
                "zh-CN": "本回合中，该角色下次使用技能时少花费1个元素骰。"
            }
        },
    },
}


register_class(FishAndChips_4_3 | FishAndChipsStatus_4_3, desc)
