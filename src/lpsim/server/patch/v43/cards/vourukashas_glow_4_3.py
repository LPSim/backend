from typing import Dict, List, Literal

from .....utils.class_registry import register_class
from ....modifiable_values import DamageValue
from ....consts import DamageElementalType, DamageType, ObjectPositionType
from ....action import DrawCardAction, MakeDamageAction
from ....match import Match
from ....event import ReceiveDamageEventArguments, RoundEndEventArguments
from ....struct import Cost
from ....card.equipment.artifact.base import RoundEffectArtifactBase
from .....utils.desc_registry import DescDictType


class HeartOfKhvarenasBrilliance_4_3(RoundEffectArtifactBase):
    name: Literal["Heart of Khvarena's Brilliance"]
    version: Literal["4.3"] = "4.3"
    cost: Cost = Cost()
    max_usage_per_round: int = 1

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Match
    ) -> List[DrawCardAction]:
        if self.usage <= 0:
            # already used
            return []
        if not self.position.check_position_valid(
            event.final_damage.target_position, match, player_idx_same = True,
            charactor_idx_same = True, area_same = True,
            source_area = ObjectPositionType.CHARACTOR,
            source_is_active_charactor = True,
        ):
            # not equipped, or not self receive damage
            return []
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        if charactor.hp == 0:
            # charactor is dying
            return []
        if event.final_damage.damage_type != DamageType.DAMAGE:
            # not damage
            return []
        # draw card
        self.usage -= 1
        return [DrawCardAction(
            player_idx = self.position.player_idx,
            number = 1,
            draw_if_filtered_not_enough = True
        )]


class VourukashasGlow_4_3(HeartOfKhvarenasBrilliance_4_3):
    name: Literal["Vourukasha's Glow"]
    version: Literal["4.3"] = "4.3"
    cost: Cost = Cost(same_dice_number = 1)

    def event_handler_ROUND_END(
        self, desc: RoundEndEventArguments, match: Match
    ) -> List[MakeDamageAction]:
        if self.position.area != ObjectPositionType.CHARACTOR:
            # not equipped
            return []
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        return [MakeDamageAction(
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    target_position = charactor.position,
                    damage = -1,
                    damage_type = DamageType.HEAL,
                    damage_elemental_type = DamageElementalType.HEAL,
                    cost = Cost()
                )
            ]
        )]


desc: Dict[str, DescDictType] = {
    "ARTIFACT/Heart of Khvarena's Brilliance": {
        "names": {
            "en-US": "Heart of Khvarena's Brilliance",
            "zh-CN": "灵光明烁之心"
        },
        "descs": {
            "4.3": {
                "en-US": "After this character takes DMG: Draw 1 card. (Once per Round)\n(A character can equip a maximum of 1 Artifact)",  # noqa: E501
                "zh-CN": "角色受到伤害后：如果所附属角色为「出战角色」，则抓1张牌。（每回合1次）\n（角色最多装备1件「圣遗物」）"  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Artifact_Huashen.png",  # noqa: E501
        "id": 312021
    },
    "ARTIFACT/Vourukasha's Glow": {
        "names": {
            "en-US": "Vourukasha's Glow",
            "zh-CN": "花海甘露之光"
        },
        "descs": {
            "4.3": {
                "en-US": "After this character takes DMG: Draw 1 card. (Once per Round)\nEnd Phase: Heal the attached character for 1 HP.\n(A character can equip a maximum of 1 Artifact)",  # noqa: E501
                "zh-CN": "角色受到伤害后：如果所附属角色为「出战角色」，则抓1张牌。（每回合1次）\n结束阶段：治疗所附属角色1点。\n（角色最多装备1件「圣遗物」）"  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Artifact_Huashentao.png",  # noqa: E501
        "id": 312022
    },
}


register_class(VourukashasGlow_4_3 | HeartOfKhvarenasBrilliance_4_3, desc)
