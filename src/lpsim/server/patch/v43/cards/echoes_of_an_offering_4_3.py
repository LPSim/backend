from typing import Dict, List, Literal

from .....utils.class_registry import register_class
from ....consts import ELEMENT_TO_DIE_COLOR, ObjectPositionType, SkillType
from ....charactor.charactor_base import SkillBase
from ....action import Actions, CreateDiceAction, DrawCardAction
from ....match import Match
from ....event import RoundPrepareEventArguments, SkillEndEventArguments
from ....struct import Cost
from ....card.equipment.artifact.base import RoundEffectArtifactBase
from .....utils.desc_registry import DescDictType


class FlowingRings_4_3(RoundEffectArtifactBase):
    name: Literal["Flowing Rings"]
    version: Literal["4.3"] = "4.3"
    cost: Cost = Cost()
    max_usage_per_round: int = 1

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Match
    ) -> List[DrawCardAction]:
        if self.usage == 0:
            # already used
            return []
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL,
            source_area = ObjectPositionType.CHARACTOR
        ):
            # not self, or not equipped
            return []
        skill: SkillBase = match.get_object(
            event.action.position)  # type: ignore
        assert skill is not None
        if skill.skill_type != SkillType.NORMAL_ATTACK:
            # not normal attack
            return []
        self.usage -= 1
        return [DrawCardAction(
            player_idx = self.position.player_idx,
            number = 1,
            draw_if_filtered_not_enough = True
        )]


class EchoesOfAnOffering_4_3(FlowingRings_4_3):
    name: Literal["Echoes of an Offering"]
    version: Literal["4.3"] = "4.3"
    cost: Cost = Cost(same_dice_number = 2)
    max_usage_per_round: int = 1

    generate_die_usage: int = 1
    max_generate_die_usage_per_round: int = 1

    def equip(self, match: Match) -> List[Actions]:
        self.usage = self.max_usage_per_round
        self.generate_die_usage = self.max_generate_die_usage_per_round
        return []

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Match
    ) -> List[Actions]:
        self.usage = self.max_usage_per_round
        self.generate_die_usage = self.max_generate_die_usage_per_round
        return []

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Match
    ) -> List[DrawCardAction | CreateDiceAction]:
        ret: List[DrawCardAction | CreateDiceAction] = []
        ret += super().event_handler_SKILL_END(event, match)
        if self.generate_die_usage == 0:
            # already used
            return ret
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL,
            source_area = ObjectPositionType.CHARACTOR
        ):
            # not self, or not equipped
            return ret
        table = match.player_tables[self.position.player_idx]
        if len(table.dice.colors) > len(table.hands):
            # dice more than hand
            return ret
        charactor = table.charactors[self.position.charactor_idx]
        # create die
        self.generate_die_usage -= 1
        ret.append(CreateDiceAction(
            player_idx = self.position.player_idx,
            color = ELEMENT_TO_DIE_COLOR[charactor.element],
            number = 1
        ))
        return ret


desc: Dict[str, DescDictType] = {
    "ARTIFACT/Flowing Rings": {
        "names": {
            "en-US": "Flowing Rings",
            "zh-CN": "浮溯之珏"
        },
        "descs": {
            "4.3": {
                "en-US": "After the character uses a Normal Attack: Draw 1 card. (Once per Round)\n(A character can equip a maximum of 1 Artifact)",  # noqa: E501
                "zh-CN": "角色使用「普通攻击」后：抓1张牌。（每回合1次）\n（角色最多装备1件「圣遗物」）"  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Artifact_Yuxiang.png",  # noqa: E501
        "id": 312019
    },
    "ARTIFACT/Echoes of an Offering": {
        "names": {
            "en-US": "Echoes of an Offering",
            "zh-CN": "来歆余响"
        },
        "descs": {
            "4.3": {
                "en-US": "After this character uses Normal Attack: Draw 1 card. (Once per Round)\nAfter this character uses a Skill: If you do not have more Elemental Dice than cards in your Hand, you will gain 1 Elemental Die of the attached character's Type. (Once per Round)\n(A character can equip a maximum of 1 Artifact)",  # noqa: E501
                "zh-CN": "角色使用「普通攻击」后：抓1张牌。（每回合1次）\n角色使用技能后：如果我方元素骰数量不多于手牌数量，则生成1个所附属角色类型的元素骰。（每回合1次）\n（角色最多装备1件「圣遗物」）"  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Artifact_Yuxiangtao.png",  # noqa: E501
        "id": 312020
    },
}


register_class(FlowingRings_4_3 | EchoesOfAnOffering_4_3, desc)
