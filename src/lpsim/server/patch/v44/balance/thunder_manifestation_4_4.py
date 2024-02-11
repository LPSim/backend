"""
1. Lightning Rod will disappear when damage increase is triggered.
2. Talent card become a skill talent, and effect is same.
"""
from typing import Dict, List, Literal
from ....action import RemoveObjectAction
from ....event import AfterMakeDamageEventArguments, MakeDamageEventArguments
from ....match import Match
from ....patch.v43.characters.thunder_manifestation_4_3 import (
    GrievingEcho_4_3,
    LightningProbe,
    LightningRod_4_3,
    LightningStrikeProbe_4_3,
    StrifefulLightning,
    ThunderManifestation_4_3,
    ThunderingShackles,
)
from ....status.character_status.base import UsageCharacterStatus
from ....character.character_base import SkillTalent
from ....struct import Cost
from .....utils.class_registry import register_class
from ....character.character_base import ElementalNormalAttackBase
from ....consts import ELEMENT_TO_DAMAGE_TYPE, DieColor
from .....utils.desc_registry import DescDictType


class LightningStrikeProbe_4_4(LightningStrikeProbe_4_3):
    version: Literal["4.4"] = "4.4"


class LightningRod_4_4(LightningRod_4_3, UsageCharacterStatus):
    version: Literal["4.4"] = "4.4"

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Match
    ) -> List[RemoveObjectAction]:
        # do nor remove in make damage event, so talent can work
        return []

    def event_handler_AFTER_MAKE_DAMAGE(
        self, event: AfterMakeDamageEventArguments, match: Match
    ) -> List[RemoveObjectAction]:
        return self.check_should_remove()


class LightningProbe_4_4(LightningProbe):
    name: Literal["Lightning Probe"] = "Lightning Probe"
    version: Literal["4.4"] = "4.4"


class GrievingEcho_4_4(SkillTalent, GrievingEcho_4_3):
    version: Literal["4.4"] = "4.4"
    character_name: Literal["Thunder Manifestation"] = "Thunder Manifestation"
    skill: Literal["Strifeful Lightning"] = "Strifeful Lightning"
    cost: Cost = Cost(
        elemental_dice_color=DieColor.ELECTRO,
        elemental_dice_number=3,
    )


class ThunderManifestation_4_4(ThunderManifestation_4_3):
    version: Literal["4.4"] = "4.4"
    skills: List[
        ElementalNormalAttackBase
        | StrifefulLightning
        | ThunderingShackles
        | LightningProbe_4_4
    ] = []

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name="Thunderous Wingslash",
                damage_type=ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost=ElementalNormalAttackBase.get_cost(self.element),
            ),
            StrifefulLightning(),
            ThunderingShackles(),
            LightningProbe_4_4(),
        ]


desc: Dict[str, DescDictType] = {
    "CHARACTER/Thunder Manifestation": {"descs": {"4.4": {"en-US": "", "zh-CN": ""}}},
    "SKILL_Thunder Manifestation_NORMAL_ATTACK/Thunderous Wingslash": {
        "descs": {
            "4.4": {"en-US": "Deals 1 Electro DMG.", "zh-CN": "造成1点雷元素伤害。"}
        }
    },
    "SKILL_Thunder Manifestation_ELEMENTAL_SKILL/Strifeful Lightning": {
        "descs": {
            "4.4": {
                "en-US": "Deals 3 Electro DMG to opposing characters affected by Lightning Rod. (If there are no eligible opposing characters, deals DMG to the active character instead)",  # noqa: E501
                "zh-CN": "对附属有雷鸣探知的敌方角色造成3点雷元素伤害。（如果敌方不存在符合条件角色，则改为对出战角色造成伤害）",  # noqa: E501
            }
        }
    },
    "CHARACTER_STATUS/Lightning Rod": {
        "descs": {
            "4.4": {
                "en-US": "While this status is active, can be triggered once and remove this status: DMG received by the attached character from Thunder Manifestation or its summons is increased by 1.\n(Only one of this status can exist on the field at once. Some of Thunder Manifestation's skills will target the character to which this is attached.)",  # noqa: E501
                "zh-CN": "此状态存在期间，可以触发1次并移除此状态：所附属角色受到雷音权现及其召唤物造成的伤害+1。\n（同一方场上最多存在一个此状态。雷音权现的部分技能，会以所附属角色为目标。）",  # noqa: E501
            }
        }
    },
    "SKILL_Thunder Manifestation_ELEMENTAL_BURST/Thundering Shackles": {
        "descs": {
            "4.4": {
                "en-US": "Deals 2 Electro DMG, summons 1 Thundering Shackles.",
                "zh-CN": "造成2点雷元素伤害，召唤轰雷禁锢。",
            }
        }
    },
    "SKILL_Thunder Manifestation_PASSIVE/Lightning Probe": {
        "descs": {
            "4.4": {
                "en-US": "(Passive) When battle begins, create a Lightning Strike Probe on the opponent's side of the field.",  # noqa: E501
                "zh-CN": "【被动】战斗开始时，在敌方场上生成雷霆探针。",
            }
        }
    },
    "TEAM_STATUS/Lightning Strike Probe": {
        "descs": {
            "4.4": {
                "en-US": "After a character on whose side of the field this card is on uses a Skill: Attach Lightning Rod to the active character on that side. (Once per Round)",  # noqa: E501
                "zh-CN": "所在阵营角色使用技能后：对所在阵营出战角色附属雷鸣探知。（每回合1次）",
            }
        },
    },
    "TALENT_Thunder Manifestation/Grieving Echo": {
        "descs": {
            "4.4": {
                "en-US": "Combat Action: When your active character is Thunder Manifestation, equip this card. After Thunder Manifestation equips this card, immediately use Strifeful Lightning. When Thunder Manifestation, with this card equipped, is in play, when opponents with Lightning Rod attached take DMG: You draw 1 card (Once per Round)\n(Your deck must contain Thunder Manifestation to add this card to your deck)",  # noqa: E501
                "zh-CN": "战斗行动：我方出战角色为雷音权现时，装备此牌。雷音权现装备此牌后，立刻使用一次雷墙倾轧。装备有此牌的雷音权现在场，附属有雷鸣探知的敌方角色受到伤害时：我方抓1张牌。（每回合1次）\n（牌组中包含雷音权现，才能加入牌组）",  # noqa: E501
            }
        },
    },
}


register_class(
    LightningRod_4_4
    | LightningStrikeProbe_4_4
    | GrievingEcho_4_4
    | ThunderManifestation_4_4,
    desc,
)
