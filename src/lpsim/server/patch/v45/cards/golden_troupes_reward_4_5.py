from typing import Dict, List, Literal
from lpsim.server.action import Actions

from lpsim.server.card.equipment.artifact.base import ArtifactBase
from lpsim.server.consts import CostLabels
from lpsim.server.event import RoundEndEventArguments
from lpsim.server.match import Match
from lpsim.server.modifiable_values import CostValue
from lpsim.server.struct import Cost
from lpsim.utils.class_registry import register_class
from lpsim.utils.desc_registry import DescDictType


class GoldenTroupesReward_4_5(ArtifactBase):
    name: Literal["Golden Troupe's Reward"] = "Golden Troupe's Reward"
    version: Literal["4.5"] = "4.5"
    cost: Cost = Cost()
    usage: int = 0
    max_usage: int = 2

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Match
    ) -> List[Actions]:
        if self.position.satisfy("source area=character active=false", match=match):
            self.usage = min(self.usage + 1, self.max_usage)
        return []

    def value_modifier_COST(
        self, value: CostValue, match: Match, mode: Literal["TEST", "REAL"]
    ) -> CostValue:
        """
        If self use any skill, or equip talent, cost decrease based on self usage.
        """
        if not self._check_value_self_skill_or_talent(
            value, match, CostLabels.ELEMENTAL_SKILL.value
        ):
            return value
        # decrease cost
        for _ in range(self.usage):
            if value.cost.decrease_cost(value.cost.elemental_dice_color):
                if mode == "REAL":
                    self.usage -= 1
        return value


desc: Dict[str, DescDictType] = {
    "ARTIFACT/Golden Troupe's Reward": {
        "names": {"en-US": "Golden Troupe's Reward", "zh-CN": "黄金剧团的奖赏"},
        "descs": {
            "4.5": {
                "en-US": 'End Phase: If the character to which this is attached is on standby, this card gains 1 "Recompense" point. (Max 2 points)\nWhen you play a Talent card or a Character uses an Elemental Skill: For each "Recompense" point this card has, consume it to spend 1 less Elemental Die.\n(A character can equip a maximum of 1 Artifact)',  # noqa: E501
                "zh-CN": "结束阶段：如果所附属角色在后台，则此牌累积1点「报酬」。（最多累积2点）\n对角色打出「天赋」或角色使用「元素战技」时：此牌每有1点「报酬」，就将其消耗，以少花费1个元素骰。\n（角色最多装备1件「圣遗物」）",  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Artifact_HuangjinjutuanXiaojian.png",  # noqa: E501
        "id": 312025,
    },
}


register_class(GoldenTroupesReward_4_5, desc)
