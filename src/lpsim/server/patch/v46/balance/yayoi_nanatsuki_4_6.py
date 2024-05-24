from typing import Dict, Literal

from pydantic import PrivateAttr
from lpsim.server.card.support.companions import RoundEffectCompanionBase
from lpsim.server.consts import CostLabels, ObjectPositionType
from lpsim.server.match import Match
from lpsim.server.modifiable_values import CostValue
from lpsim.server.struct import Cost
from lpsim.utils.class_registry import register_class
from lpsim.utils.desc_registry import DescDictType


class YayoiNanatsuki_4_6(RoundEffectCompanionBase):
    name: Literal["Yayoi Nanatsuki"]
    version: Literal["4.6"] = "4.6"
    cost: Cost = Cost(same_dice_number=1)
    max_usage_per_round: int = 1
    _card_cost_label: int = PrivateAttr(CostLabels.ARTIFACT.value)

    def value_modifier_COST(
        self, value: CostValue, match: Match, mode: Literal["REAL", "TEST"]
    ) -> CostValue:
        """
        If has usage, and self use weapon card, decrease.
        """
        if self.position.area != ObjectPositionType.SUPPORT:
            # not in support area, do nothing
            return value
        if self.usage <= 0:
            # no usage
            return value
        if value.position.player_idx != self.position.player_idx:
            # not self player
            return value
        if value.cost.label & self._card_cost_label == 0:
            # not corresponding card
            return value
        # decrease
        equipped_number = 0
        table = match.player_tables[self.position.player_idx]
        for character in table.characters:
            if (
                character.artifact is not None
                and self._card_cost_label & CostLabels.ARTIFACT.value > 0
            ):
                equipped_number += 1
        decrease_number = 1 + (equipped_number >= 2)
        result = []
        for _ in range(decrease_number):
            result.append(value.cost.decrease_cost(None))
        if True in result:
            if mode == "REAL":
                self.usage -= 1
        return value


desc: Dict[str, DescDictType] = {
    "SUPPORT/Yayoi Nanatsuki": {
        "descs": {
            "4.6": {
                "zh-CN": "我方打出「圣遗物」手牌时：少花费1个元素骰；我方场上已有2个已装备「圣遗物」的角色，就额外少花费1个元素骰。（每回合1次）",  # noqa
                "en-US": "When playing an Artifact card: Spend 1 less Elemental Die. On top of that, if the number of your characters already equipped with an artifact on the field is greater than 2, you spend 1 less Elemental Die. (Once per Round.)",  # noqa
            }
        },
    },
}


register_class(YayoiNanatsuki_4_6, desc)
