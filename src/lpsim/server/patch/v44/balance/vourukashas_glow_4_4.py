from typing import Dict, List, Literal

from ....action import MakeDamageAction
from ....event import RoundEndEventArguments
from ....struct import Cost
from ....patch.v43.cards.vourukashas_glow_4_3 import VourukashasGlow_4_3
from ....match import Match
from .....utils import register_class, DescDictType


class VourukashasGlow_4_4(VourukashasGlow_4_3):
    name: Literal["Vourukasha's Glow"]
    version: Literal["4.4"] = "4.4"
    cost: Cost = Cost(same_dice_number=1)

    def event_handler_ROUND_END(
        self, desc: RoundEndEventArguments, match: Match
    ) -> List[MakeDamageAction]:
        if self.usage == self.max_usage_per_round:
            # not draw card, return
            return []
        return super().event_handler_ROUND_END(desc, match)


desc: Dict[str, DescDictType] = {
    "ARTIFACT/Vourukasha's Glow": {
        "descs": {
            "4.4": {
                "en-US": 'After this character takes DMG: Draw 1 card. (Once per Round)\nEnd Phase: If this character has triggered the effect "Draw 1 card" this round: heal the attached character for 1 HP.\n(A character can equip a maximum of 1 Artifact)',  # noqa: E501
                "zh-CN": "角色受到伤害后：如果所附属角色为「出战角色」，则抓1张牌。（每回合1次）\n结束阶段：若本角色在回合内触发了抓1张牌的效果，治疗所附属角色1点。\n（角色最多装备1件「圣遗物」）",  # noqa: E501
            }
        },
    },
}


register_class(VourukashasGlow_4_4, desc)
