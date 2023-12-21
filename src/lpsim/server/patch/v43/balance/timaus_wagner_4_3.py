from typing import Dict, List, Literal
from pydantic import PrivateAttr

from ....action import DrawCardAction
from .....utils.class_registry import register_class
from .....utils.desc_registry import DescDictType
from ....match import Match

from ....consts import CostLabels
from ....card.support.companions import Timaeus_3_3


class Timaeus_4_3(Timaeus_3_3):
    version: Literal["4.3"] = "4.3"
    decrease_target: int = CostLabels.ARTIFACT.value
    _check_type: Literal["TYPE", "NUMBER"] = PrivateAttr("NUMBER")
    _check_number: int = PrivateAttr(6)

    def play(self, match: Match) -> List[DrawCardAction]:
        if self._check_type == "NUMBER":
            counter = 0
            for card in match.player_tables[
                self.position.player_idx
            ].player_deck_information.cards:
                if card.cost_label & self.decrease_target != 0:
                    counter += 1
            if counter >= self._check_number:
                return [
                    DrawCardAction(
                        player_idx = self.position.player_idx,
                        number = 1,
                        whitelist_cost_labels = self.decrease_target,
                        draw_if_filtered_not_enough = False,
                    )
                ]
        else:
            assert self._check_type == "TYPE"
            names = set()
            for card in match.player_tables[
                self.position.player_idx
            ].player_deck_information.cards:
                if card.cost_label & self.decrease_target != 0:
                    names.add(card.name)
            if len(names) >= self._check_number:
                return [
                    DrawCardAction(
                        player_idx = self.position.player_idx,
                        number = 1,
                        whitelist_cost_labels = self.decrease_target,
                        draw_if_filtered_not_enough = False,
                    )
                ]
        return []


class Wagner_4_3(Timaeus_4_3):
    name: Literal["Wagner"] = "Wagner"
    decrease_target: int = CostLabels.WEAPON.value
    _check_type: Literal["TYPE", "NUMBER"] = PrivateAttr("TYPE")
    _check_number: int = PrivateAttr(3)


desc: Dict[str, DescDictType] = {
    "SUPPORT/Wagner": {
        "descs": {
            "4.3": {
                "zh-CN": "入场时附带2个「锻造原胚」。结束阶段：补充1个「锻造原胚」。入场时：如果牌组中携带了至少3种「武器」，从牌组中随机抽取1张「武器」。打出「武器」手牌时：如可能，则支付等同于「武器」总费用数量的「锻造原胚」，以免费装备此「武器」。（每回合1次）",  # noqa: E501
                "en-US": "Comes with 2 Forging Billet when played. End Phase: Gain 1 Forging Billet. When played: If you have not less than 3 types of Weapons in your initial deck, draw 1 Weapon from your deck. When playing a Weapon Card: If possible, spend Forging Billet equal to the total cost of the Weapon and equip this Weapon for free. (Once per Round)",  # noqa: E501
            }
        },
    },
    "SUPPORT/Timaeus": {
        "descs": {
            "4.3": {
                "zh-CN": "入场时附带2个「合成材料」。结束阶段：补充1个「合成材料」。入场时：如果牌组中携带了至少6张「圣遗物」，从牌组中随机抽取1张「圣遗物」。打出「圣遗物」手牌时：如可能，则支付等同于「圣遗物」总费用数量的「合成材料」，以免费装备此「圣遗物」。（每回合1次）",  # noqa: E501
                "en-US": "Comes with 2 Transmutation Materials when played. When played: If you have not less than 6 Artifacts in your initial deck, draw 1 Artifact from your deck. End Phase: Gain 1 Transmutation Material. When playing an Artifact Card: If possible, spend Transmutation Materials equal to the total cost of the Artifact and equip this Artifact for free. (Once per Round)",  # noqa: E501
            }
        },
    },
}


register_class(Timaeus_4_3 | Wagner_4_3, desc)
