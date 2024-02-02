from typing import Dict, List, Literal

from .....utils.class_registry import register_class
from ....consts import ELEMENT_TO_DIE_COLOR, DieColor
from ....match import Match
from ....action import CreateDiceAction
from ....struct import Cost
from ....card.equipment.artifact.gilded_dreams import ShadowOfTheSandKing_4_2
from .....utils.desc_registry import DescDictType


class GildedDreams_4_3(ShadowOfTheSandKing_4_2):
    name: Literal["Gilded Dreams"]
    version: Literal["4.3"] = "4.3"
    cost: Cost = Cost(any_dice_number=3)
    max_usage_per_round: int = 2

    def equip(self, match: Match) -> List[CreateDiceAction]:
        """
        When equipped, create one elemental dice. If there are 3 different
        elemental dice in your team, create one omni dice.
        """
        super().equip(match)
        characters = match.player_tables[self.position.player_idx].characters
        equip_character = characters[self.position.character_idx]
        ret: List[CreateDiceAction] = [
            CreateDiceAction(
                player_idx=self.position.player_idx,
                number=1,
                color=ELEMENT_TO_DIE_COLOR[equip_character.element],
            )
        ]
        elements = set()
        for character in characters:
            elements.add(character.element)
        if len(elements) >= 3:
            ret.append(
                CreateDiceAction(
                    player_idx=self.position.player_idx, number=1, color=DieColor.OMNI
                )
            )
        return ret


desc: Dict[str, DescDictType] = {
    "ARTIFACT/Gilded Dreams": {
        "names": {"en-US": "Gilded Dreams", "zh-CN": "饰金之梦"},
        "descs": {
            "4.3": {
                "en-US": "When played: generate 1 Die of the same Element as the attached character. If you have 3 different Elemental Types in your party, generate 1 Omni Element in addition to this.\nWhen the character to which this card is attached is your active character, then when an opposing character takes Elemental Reaction DMG: Draw a card. (Twice per Round)\n(A character can equip a maximum of 1 Artifact)",  # noqa: E501
                "zh-CN": "入场时：生成1个所附属角色类型的元素骰。如果我方队伍中存在3种不同元素类型的角色，则额外生成1个万能元素。\n所附属角色为出战角色期间，敌方受到元素反应伤害时：抓1张牌。（每回合至多2次）\n（角色最多装备1件「圣遗物」）",  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Artifact_Chiwangtao.png",  # noqa: E501
        "id": 312018,
    },
}


register_class(GildedDreams_4_3, desc)
