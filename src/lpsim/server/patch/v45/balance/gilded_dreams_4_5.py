from typing import Dict, Literal, List

from lpsim.server.consts import ELEMENT_TO_DIE_COLOR
from lpsim.server.action import CreateDiceAction
from lpsim.server.patch.v43.cards.gilded_dreams_4_3 import GildedDreams_4_3
from lpsim.server.struct import Cost
from lpsim.server import Match
from lpsim.utils.class_registry import register_class
from lpsim.utils.desc_registry import DescDictType


class GildedDreams_4_5(GildedDreams_4_3):
    version: Literal["4.5"] = "4.5"
    cost: Cost = Cost(same_dice_number=3)

    def equip(self, match: Match) -> List[CreateDiceAction]:
        """
        When equipped, create one elemental dice. If there are 3 different
        elemental dice in your team, create 2 dice.
        """
        super().equip(match)
        characters = match.player_tables[self.position.player_idx].characters
        equip_character = characters[self.position.character_idx]
        ret: CreateDiceAction = CreateDiceAction(
            player_idx=self.position.player_idx,
            number=1,
            color=ELEMENT_TO_DIE_COLOR[equip_character.element],
        )
        elements = set()
        for character in characters:
            elements.add(character.element)
        if len(elements) >= 3:
            ret.number = 2
        return [ret]


desc: Dict[str, DescDictType] = {
    "ARTIFACT/Gilded Dreams": {
        "descs": {
            "4.5": {
                "en-US": "When played: generate 1 Die of the same Element as the attached character. If you have 3 different Elemental Types in your party, generate 2 Dice of the same Element as the attached character.\nWhen the character to which this card is attached is your active character, then when an opposing character takes Elemental Reaction DMG: Draw a card. (Twice per Round)\n(A character can equip a maximum of 1 Artifact)",  # noqa: E501
                "zh-CN": "入场时：生成1个所附属角色类型的元素骰。如果我方队伍中存在3种不同元素类型的角色，则生成2个所附属角色类型的元素骰。\n所附属角色为出战角色期间，敌方受到元素反应伤害时：抓1张牌。（每回合至多2次）\n（角色最多装备1件「圣遗物」）",  # noqa: E501
            }
        },
    },
}


register_class(GildedDreams_4_5, desc)
