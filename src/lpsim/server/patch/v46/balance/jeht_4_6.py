from typing import Dict, List, Literal
from pydantic import PrivateAttr

from lpsim.server.modifiable_values import CostValue
from lpsim.server.match import Match
from lpsim.server.action import CreateObjectAction, RemoveObjectAction
from lpsim.server.event import (
    SkillEndEventArguments,
    UseSkillEventArguments,
)
from lpsim.server.consts import IconType, ObjectPositionType, SkillType
from lpsim.server.status.character_status.base import UsageCharacterStatus
from lpsim.server.struct import Cost
from lpsim.utils.class_registry import register_class
from lpsim.utils.desc_registry import DescDictType

from lpsim.server.patch.v44.cards.jeht_4_4 import Jeht_4_4


class SandAndDreams_4_6(UsageCharacterStatus):
    name: Literal["Sand and Dreams"] = "Sand and Dreams"
    version: Literal["4.6"] = "4.6"
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.BUFF] = IconType.BUFF

    def value_modifier_COST(
        self, value: CostValue, match: Match, mode: Literal["TEST", "REAL"]
    ) -> CostValue:
        """
        If self use skill, or equip talent, cost -2.
        """
        if not self._check_value_self_skill_or_talent(value, match):
            return value
        # decrease cost
        assert self.usage > 0
        decrease_result = [
            value.cost.decrease_cost(value.cost.elemental_dice_color),
            value.cost.decrease_cost(value.cost.elemental_dice_color),
            value.cost.decrease_cost(value.cost.elemental_dice_color),
        ]
        if True in decrease_result:  # pragma: no branch
            # decrease cost success
            if mode == "REAL":
                self.usage -= 1
        return value

    def event_handler_USE_SKILL(
        self, event: UseSkillEventArguments, match: Match
    ) -> List[RemoveObjectAction]:
        return self.check_should_remove()


class Jeht_4_6(Jeht_4_4):
    name: Literal["Jeht"]
    version: Literal["4.6"] = "4.6"
    usage: int = 0
    _max_usage: int = PrivateAttr(6)
    icon_type: Literal[IconType.TIMESTATE] = IconType.TIMESTATE
    cost: Cost = Cost(same_dice_number=1)

    handler_name: Literal["Jeht"] = "Jeht"

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Match
    ) -> List[CreateObjectAction | RemoveObjectAction]:
        if not self.position.check_position_valid(
            event.action.position,
            match,
            player_idx_same=True,
            target_area=ObjectPositionType.SKILL,
        ):
            # not self use skill
            return []
        if self.usage < 6:
            # not enough usage
            return []
        if event.action.skill_type != SkillType.ELEMENTAL_BURST:
            # not use elemental burst
            return []
        # discard self and create dice
        target = self.query_one(match, "our active")
        assert target is not None
        return [
            CreateObjectAction(
                object_name="Sand and Dreams",
                object_position=target.position.set_area(
                    ObjectPositionType.CHARACTER_STATUS
                ),
                object_arguments={},
            ),
            RemoveObjectAction(object_position=self.position),
        ]


desc: Dict[str, DescDictType] = {
    "SUPPORT/Jeht": {
        "descs": {
            "4.6": {
                "en-US": "This card will record the number of cards discarded from your Support Zone during this match as Sophistication points. (Max 6 points)\nAfter your characters use an Elemental Burst: If this card has recorded at least 6 Sophistication points, discard this card and attach Sand and Dreams to your active character.",  # noqa: E501
                "zh-CN": "此牌会记录本场对局中我方支援区弃置卡牌的数量，称为「阅历」。（最多6点）\n我方角色使用「元素爆发」后：如果「阅历」至少为6，则弃置此牌，对我方出战角色附属沙与梦。",  # noqa: E501
            }
        },
    },
    "CHARACTER_STATUS/Sand and Dreams": {
        "names": {
            "en-US": "Sand and Dreams",
            "zh-CN": "沙与梦",
        },
        "descs": {
            "4.6": {
                "en-US": "When you play a Talent card or a Character uses a Skill: Spend 3 less Elemental Dice.\nUsages: 1",  # noqa: E501
                "zh-CN": "对角色打出「天赋」或角色使用技能时：少花费3个元素骰。\n可用次数：1",
            }
        },
    },
}


register_class(Jeht_4_6 | SandAndDreams_4_6, desc)
