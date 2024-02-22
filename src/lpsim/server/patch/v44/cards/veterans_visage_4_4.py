from typing import Dict, List, Literal
from ....struct import Cost

from .....utils.class_registry import register_class
from ....consts import ELEMENT_TO_DIE_COLOR, DamageType, ObjectPositionType
from ....action import Actions, CreateDiceAction, DrawCardAction
from ....match import Match
from ....event import ReceiveDamageEventArguments
from ....card.equipment.artifact.base import RoundEffectArtifactBase
from .....utils.desc_registry import DescDictType


class VeteransVisage_4_4(RoundEffectArtifactBase):
    name: Literal["Veteran's Visage"]
    version: Literal["4.4"] = "4.4"
    cost: Cost = Cost(any_dice_number=2)
    max_usage_per_round: int = 2

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Match
    ) -> List[Actions]:
        if self.usage <= 0:
            # already used
            return []
        if not self.position.check_position_valid(
            event.final_damage.target_position,
            match,
            player_idx_same=True,
            character_idx_same=True,
            area_same=True,
            source_area=ObjectPositionType.CHARACTER,
        ):
            # not equipped, or not self receive damage
            return []
        character = match.player_tables[self.position.player_idx].characters[
            self.position.character_idx
        ]
        if character.hp == 0:
            # character is dying
            return []
        if event.final_damage.damage_type not in [DamageType.DAMAGE, DamageType.HEAL]:
            # not damage or heal
            return []
        if self.usage == 2:
            # create die
            self.usage -= 1
            character = match.player_tables[self.position.player_idx].characters[
                self.position.character_idx
            ]
            return [
                CreateDiceAction(
                    player_idx=self.position.player_idx,
                    color=ELEMENT_TO_DIE_COLOR[character.element],
                    number=1,
                )
            ]
        else:
            # draw card
            self.usage -= 1
            return [
                DrawCardAction(
                    player_idx=self.position.player_idx,
                    number=1,
                    draw_if_filtered_not_enough=True,
                )
            ]


desc: Dict[str, DescDictType] = {
    "ARTIFACT/Veteran's Visage": {
        "names": {"en-US": "Veteran's Visage", "zh-CN": "老兵的容颜"},
        "descs": {
            "4.4": {
                "en-US": "After this character takes DMG or is healed: Based on the number of times this effect has been triggered this Round, the effects will be different.\nFirst Trigger: Create 1 Elemental Die of the character's Elemental Type.\nSecond Trigger: Draw 1 card.\n(A character can equip a maximum of 1 Artifact)",  # noqa: E501
                "zh-CN": "角色受到伤害或治疗后：根据本回合触发此效果的次数，执行不同的效果。\n第一次触发：生成1个此角色类型的元素骰。\n第二次触发：抓1张牌。\n（角色最多装备1件「圣遗物」）",  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Artifact_LaobinDanjian.png",  # noqa: E501
        "id": 312023,
    },
}


register_class(VeteransVisage_4_4, desc)
