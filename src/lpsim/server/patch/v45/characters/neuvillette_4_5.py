from typing import Any, Dict, List, Literal

from lpsim.server.query import query_one
from lpsim.server.consts import IconType
from lpsim.server.status.character_status.base import (
    PrepareCharacterStatus,
    UsageCharacterStatus,
)
from lpsim.server.status.team_status.base import UsageTeamStatus
from lpsim.utils.class_registry import register_class
from lpsim.server.match import Match
from lpsim.utils.desc_registry import DescDictType
from lpsim.server.modifiable_values import DamageIncreaseValue, DamageValue
from lpsim.server.event import ReceiveDamageEventArguments, SkillEndEventArguments
from lpsim.server.action import Actions, CreateObjectAction, MakeDamageAction
from lpsim.server.struct import Cost
from lpsim.consts import (
    ELEMENT_TO_DAMAGE_TYPE,
    DamageElementalType,
    DieColor,
    ElementType,
    FactionType,
    ObjectPositionType,
    WeaponType,
)
from lpsim.server.character.character_base import (
    AOESkillBase,
    ElementalBurstBase,
    ElementalNormalAttackBase,
    ElementalSkillBase,
    CharacterBase,
    SkillTalent,
)


# Character status.


# Round status, will last for several rounds and disappear
class HeirToTheAncientSeasAuthorityStatus_4_5(UsageCharacterStatus):
    name: Literal[
        "Heir to the Ancient Sea's Authority"
    ] = "Heir to the Ancient Sea's Authority"
    version: Literal["4.5"] = "4.5"
    usage: int = 2
    max_usage: int = 2
    icon_type: IconType = IconType.ATK_UP

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Match, mode: Literal["TEST", "REAL"]
    ) -> DamageIncreaseValue:
        """
        When this character attack, increase one damage.
        """
        if self.usage <= 0:
            return value
        if not value.is_corresponding_character_use_damage_skill(
            self.position, match, None
        ):
            return value
        value.damage += 1
        self.usage -= 1
        return value


# Usage status, will not disappear until usage is 0
class SourcewaterDroplet_4_5(UsageTeamStatus):
    name: Literal["Sourcewater Droplet"] = "Sourcewater Droplet"
    version: Literal["4.5"] = "4.5"
    usage: int = 1
    max_usage: int = 3
    icon_type: IconType = IconType.OTHERS

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Match
    ) -> List[Actions]:
        # when Neuvillette uses As Water Seeks Equilibrium, heal 2 hp and prepare skill
        who = query_one(event.action.position, match, "self")
        if (
            who is not None
            and who.name == "Neuvillette"
            and event.action.skill_type == "NORMAL_ATTACK"
            and who.position.player_idx == self.position.player_idx
        ):
            self.usage -= 1
            return [
                MakeDamageAction(
                    damage_value_list=[
                        DamageValue.create_heal(self.position, who.position, -2, Cost())
                    ]
                ),
                CreateObjectAction(
                    object_name="Equitable Judgment",
                    object_position=who.position.set_area(
                        ObjectPositionType.CHARACTER_STATUS
                    ),
                    object_arguments={},
                ),
            ]
        return []


# class IncinerationDrive_4_1(PrepareCharacterStatus):
class EquitableJudgment_4_5(PrepareCharacterStatus):
    name: Literal["Equitable Judgment"] = "Equitable Judgment"
    version: Literal["4.5"] = "4.5"
    character_name: Literal["Neuvillette"] = "Neuvillette"
    skill_name: Literal["Equitable Judgment"] = "Equitable Judgment"


# Skills


class EquitableJudgment(ElementalNormalAttackBase):
    name: Literal["Equitable Judgment"] = "Equitable Judgment"
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost()

    def is_valid(self, match: Any) -> bool:
        return False

    def get_actions(self, match: Any) -> List[Actions]:
        char: CharacterBase = self.query_one(match, "self")  # type: ignore
        action = self.attack_opposite_active(match, self.damage, self.damage_type)
        if char.hp >= 6:
            action.damage_value_list[0].damage += 1
            attack_self_action = self.attack_self(match, 1)
            action.damage_value_list.append(attack_self_action.damage_value_list[0])
        return [action]


class OTearsIShallRepay(ElementalSkillBase):
    name: Literal["O Tears, I Shall Repay"] = "O Tears, I Shall Repay"
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(elemental_dice_color=DieColor.HYDRO, elemental_dice_number=3)

    def get_actions(self, match: Match) -> List[Actions]:
        """
        Attack and create object
        """
        return super().get_actions(match) + [
            self.create_team_status("Sourcewater Droplet")
        ]


class OTidesIHaveReturned(ElementalBurstBase, AOESkillBase):
    name: Literal["O Tides, I Have Returned"] = "O Tides, I Have Returned"
    damage: int = 2
    back_damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(
        elemental_dice_color=DieColor.HYDRO, elemental_dice_number=3, charge=2
    )

    def get_actions(self, match: Match) -> List[Actions]:
        return super().get_actions(match) + [
            self.create_team_status("Sourcewater Droplet", {"usage": 2})
        ]


# Talents


class HeirToTheAncientSeasAuthority_4_5(SkillTalent):
    name: Literal["Heir to the Ancient Sea's Authority"]
    version: Literal["4.5"] = "4.5"
    character_name: Literal["Neuvillette"] = "Neuvillette"
    cost: Cost = Cost(
        elemental_dice_color=DieColor.HYDRO, elemental_dice_number=1, any_dice_number=2
    )
    skill: Literal["As Water Seeks Equilibrium"] = "As Water Seeks Equilibrium"

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Match
    ) -> List[CreateObjectAction]:
        if self.position.not_satisfy(
            "source area=character and both pidx=same and target area=skill",
            target=event.final_damage.position,
        ):
            # not equip, not our use skill
            return []
        if ElementType.HYDRO not in event.reacted_elements:
            # not trigger hydro reaction
            return []
        return [
            CreateObjectAction(
                object_name="Heir to the Ancient Sea's Authority",
                object_position=self.position.set_area(
                    ObjectPositionType.CHARACTER_STATUS
                ),
                object_arguments={},
            )
        ]


# character base


# character class name should contain its version.
class Neuvillette_4_5(CharacterBase):
    name: Literal["Neuvillette"]
    version: Literal["4.5"] = "4.5"
    element: ElementType = ElementType.HYDRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        ElementalNormalAttackBase
        | EquitableJudgment
        | OTearsIShallRepay
        | OTidesIHaveReturned
    ] = []
    faction: List[FactionType] = [FactionType.FONTAINE, FactionType.ARKHE_PNEUMA]
    weapon_type: WeaponType = WeaponType.CATALYST

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name="As Water Seeks Equilibrium",
                damage_type=ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost=ElementalNormalAttackBase.get_cost(self.element),
            ),
            EquitableJudgment(),
            OTearsIShallRepay(),
            OTidesIHaveReturned(),
        ]


# define descriptions of newly defined classes. Note key of skills and talents
# have character names. For balance changes, only descs are needed to define.
character_descs: Dict[str, DescDictType] = {
    "CHARACTER/Neuvillette": {
        "names": {"en-US": "Neuvillette", "zh-CN": "那维莱特"},
        "descs": {"4.5": {"en-US": "", "zh-CN": ""}},
        "image_path": "cardface/Char_Avatar_Neuvillette.png",  # noqa: E501
        "id": 1210,
    },
    "CHARACTER_STATUS/Heir to the Ancient Sea's Authority": {
        "names": {"en-US": "Heir to the Ancient Sea's Authority", "zh-CN": "遗龙之荣"},
        "descs": {
            "4.5": {
                "en-US": "This character deals +1 DMG for the next 2 instances.",
                "zh-CN": "角色接下来2次造成的伤害+1。",
            }
        },
    },
    "TALENT_Neuvillette/Heir to the Ancient Sea's Authority": {
        "names": {
            "en-US": "Heir to the Ancient Sea's Authority",
            "zh-CN": "古海孑遗的权柄",
        },
        "descs": {
            "4.5": {
                "en-US": "Combat Action: When your active character is Neuvillette, equip this card.\nAfter Neuvillette equips this card, immediately use As Water Seeks Equilibrium once.\nAfter your characters trigger Hydro-Related Reactions: Neuvillette, who has this card equipped, deals +1 DMG for the next 2 instances.\n(You must have Neuvillette in your deck to add this card to your deck.)",  # noqa: E501
                "zh-CN": "战斗行动：我方出战角色为那维莱特时，装备此牌。\n那维莱特装备此牌后，立刻使用一次如水从平。\n我方角色引发水元素相关反应后：装备有此牌的那维莱特接下来2次造成的伤害+1。\n（牌组中包含那维莱特，才能加入牌组）",  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Talent_Neuvillette.png",  # noqa: E501
        "id": 212101,
    },
    "SKILL_Neuvillette_NORMAL_ATTACK/As Water Seeks Equilibrium": {
        "names": {"en-US": "As Water Seeks Equilibrium", "zh-CN": "如水从平"},
        "descs": {
            "4.5": {"en-US": "Deals 1 Hydro DMG.", "zh-CN": "造成1点水元素伤害。"}
        },
    },
    "SKILL_Neuvillette_ELEMENTAL_SKILL/O Tears, I Shall Repay": {
        "names": {"en-US": "O Tears, I Shall Repay", "zh-CN": "泪水啊，我必偿还"},
        "descs": {
            "4.5": {
                "en-US": "Deals 2 Hydro DMG, creates 1 Sourcewater Droplet.",
                "zh-CN": "造成2点水元素伤害，生成源水之滴。",
            }
        },
    },
    "TEAM_STATUS/Sourcewater Droplet": {
        "names": {"en-US": "Sourcewater Droplet", "zh-CN": "源水之滴"},
        "descs": {
            "4.5": {
                "en-US": "After Neuvillette uses a Normal Attack: Heals the character for 2 HP. After this, Prepare Skill|s1:prepares: Equitable Judgment.\nUsage(s): 1 (Can stack. Max 3 stacks.)",  # noqa: E501
                "zh-CN": "那维莱特进行普通攻击后：治疗角色2点，然后角色准备技能：衡平推裁。\n可用次数：1（可叠加，最多叠加到3次）",  # noqa: E501
            }
        },
        "image_path": "status/Neuvillette_S.png",
    },
    "SKILL_Neuvillette_ELEMENTAL_BURST/O Tides, I Have Returned": {
        "names": {"en-US": "O Tides, I Have Returned", "zh-CN": "潮水啊，我已归来"},
        "descs": {
            "4.5": {
                "en-US": "Deals 2 Hydro DMG, deals 1 Piercing DMG to all opposing characters on standby, then creates a Sourcewater Droplet with 2 Usages.",  # noqa: E501
                "zh-CN": "造成2点水元素伤害，对所有后台敌人造成1点穿透伤害，生成可用次数为2的源水之滴。",  # noqa: E501
            }
        },
    },
    "CHARACTER_STATUS/Equitable Judgment": {
        "names": {"en-US": "Equitable Judgment", "zh-CN": "衡平推裁"},
        "descs": {
            "4.5": {
                "en-US": "(Prepare for 1 turn)\nDeals 2 Hydro DMG. If character has at least 6 HP, then they deal 1 Piercing DMG to themselves and deal +1 DMG.",  # noqa: E501
                "zh-CN": "（需准备1个行动轮）\n造成2点水元素伤害，如果生命值至少为6，则对自身造成1点穿透伤害使伤害+1。",  # noqa: E501
            }
        },
    },
    "SKILL_Neuvillette_NORMAL_ATTACK/Equitable Judgment": {
        "names": {"en-US": "Equitable Judgment", "zh-CN": "衡平推裁"},
        "descs": {
            "4.5": {
                "en-US": "(Prepare for 1 turn)\nDeals 2 Hydro DMG. If character has at least 6 HP, then they deal 1 Piercing DMG to themselves and deal +1 DMG.",  # noqa: E501
                "zh-CN": "（需准备1个行动轮）\n造成2点水元素伤害，如果生命值至少为6，则对自身造成1点穿透伤害使伤害+1。",  # noqa: E501
            }
        },
    },
}


register_class(
    Neuvillette_4_5
    | HeirToTheAncientSeasAuthority_4_5
    | HeirToTheAncientSeasAuthorityStatus_4_5
    | SourcewaterDroplet_4_5
    | EquitableJudgment_4_5,
    character_descs,
)
