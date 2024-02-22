from typing import Dict, List, Literal

from ....action import ActionTypes, Actions, MakeDamageAction, RemoveObjectAction
from .....utils.class_registry import register_class
from ....status.character_status.base import CharacterStatusBase
from ....summon.base import AttackerSummonBase
from ....modifiable_values import DamageIncreaseValue, DamageValue
from ....event import RoundPrepareEventArguments, SkillEndEventArguments
from ....match import Match
from ....struct import Cost
from ....consts import (
    DamageElementalType,
    DamageType,
    DieColor,
    ElementType,
    FactionType,
    IconType,
    ObjectPositionType,
    ObjectType,
    WeaponType,
)
from ....character.character_base import (
    CharacterBase,
    ElementalBurstBase,
    ElementalNormalAttackBase,
    ElementalSkillBase,
    PhysicalNormalAttackBase,
    SkillBase,
    SkillTalent,
)
from .....utils.desc_registry import DescDictType


class PropSurplus_4_3(CharacterStatusBase):
    name: Literal["Prop Surplus"] = "Prop Surplus"
    version: Literal["4.3"] = "4.3"
    usage: int = 1
    max_usage: int = 3
    icon_type: IconType = IconType.BUFF

    def value_modifier_DAMAGE_INCREASE(
        self,
        value: DamageIncreaseValue,
        match: Match,
        mode: Literal["TEST", "REAL"],
    ) -> DamageIncreaseValue:
        if not self.position.check_position_valid(
            value.position,
            match,
            player_idx_same=True,
            character_idx_same=True,
            target_area=ObjectPositionType.SKILL,
        ):
            # not self use skill
            return value
        source: SkillBase = match.get_object(value.position)  # type: ignore
        assert source is not None and source.type == ObjectType.SKILL
        if source.name != "Bewildering Lights":
            # not Bewildering Lights
            return value
        # increase damage by usage
        assert self.usage > 0
        assert mode == "REAL"
        value.damage += self.usage
        return value

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Match
    ) -> List[MakeDamageAction | RemoveObjectAction]:
        """
        If self use Bewildering Lights, heal self and remove self.
        """
        if not self.position.check_position_valid(
            event.action.position,
            match,
            player_idx_same=True,
            character_idx_same=True,
            target_area=ObjectPositionType.SKILL,
        ):
            # not self use skill
            return []
        source = match.get_object(event.action.position)
        assert source is not None and source.type == ObjectType.SKILL
        if source.name != "Bewildering Lights":
            # not Bewildering Lights
            return []
        # heal self and remove self
        assert self.usage > 0
        character = match.player_tables[self.position.player_idx].characters[
            self.position.character_idx
        ]
        return [
            MakeDamageAction(
                damage_value_list=[
                    DamageValue(
                        position=self.position,
                        damage_type=DamageType.HEAL,
                        target_position=character.position,
                        damage=-self.usage,
                        damage_elemental_type=DamageElementalType.HEAL,
                        cost=Cost(),
                    )
                ]
            ),
            RemoveObjectAction(
                object_position=self.position,
            ),
        ]


class GrinMalkinHat_4_3(AttackerSummonBase):
    name: Literal["Grin-Malkin Hat"] = "Grin-Malkin Hat"
    version: Literal["4.3"] = "4.3"
    damage: int = 1
    damage_elemental_type: DamageElementalType = DamageElementalType.PYRO
    usage: int = 1
    max_usage: int = 2
    renew_type: Literal["ADD"] = "ADD"


class PropArrow(ElementalNormalAttackBase):
    name: Literal["Prop Arrow"] = "Prop Arrow"
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = Cost(elemental_dice_color=DieColor.PYRO, elemental_dice_number=3)

    def get_actions(self, match: Match) -> List[Actions]:
        ret = super().get_actions(match)
        damage_action = ret[0]
        assert damage_action.type == ActionTypes.MAKE_DAMAGE
        ret += [
            self.create_summon("Grin-Malkin Hat"),
            self.create_character_status("Prop Surplus"),
        ]
        character = match.player_tables[self.position.player_idx].characters[
            self.position.character_idx
        ]
        if character.hp >= 6:
            ret.append(self.attack_self(match, 1))
        return ret


class WondrousTrickMiracleParade(ElementalBurstBase):
    name: Literal["Wondrous Trick: Miracle Parade"] = "Wondrous Trick: Miracle Parade"
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = Cost(
        elemental_dice_color=DieColor.PYRO, elemental_dice_number=3, charge=2
    )

    def get_actions(self, match: Match) -> List[Actions]:
        ret = super().get_actions(match)
        damage_action = ret[1]
        assert damage_action.type == ActionTypes.MAKE_DAMAGE
        ret += [
            self.create_summon("Grin-Malkin Hat"),
            self.create_character_status("Prop Surplus"),
        ]
        return ret


class ConclusiveOvation_4_3(SkillTalent):
    name: Literal["Conclusive Ovation"]
    character_name: Literal["Lyney"] = "Lyney"
    version: Literal["4.3"] = "4.3"
    skill: Literal["Prop Arrow"] = "Prop Arrow"
    usage: int = 1
    cost: Cost = Cost(elemental_dice_color=DieColor.PYRO, elemental_dice_number=3)

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Match
    ) -> List[Actions]:
        """
        Reset usage
        """
        self.usage = 1
        return []

    def value_modifier_DAMAGE_INCREASE(
        self,
        value: DamageIncreaseValue,
        match: Match,
        mode: Literal["TEST", "REAL"],
    ) -> DamageIncreaseValue:
        if self.position.area != ObjectPositionType.CHARACTER:
            # not equipped
            return value
        if self.usage == 0:
            # no usage left
            return value
        if value.position.player_idx != self.position.player_idx:
            # not self
            return value
        if value.target_position.player_idx == self.position.player_idx:
            # self target self
            return value
        target: CharacterBase = match.get_object(value.target_position)  # type: ignore
        assert target is not None
        if ElementType.PYRO not in target.element_application:
            # target have no pyro
            return value
        source = match.get_object(value.position)
        if source is not None and source.type == ObjectType.SKILL:
            # is skill, find corresponding character
            source = match.player_tables[value.position.player_idx].characters[
                value.position.character_idx
            ]
        if source is None or source.name not in ["Lyney", "Grin-Malkin Hat"]:
            # not from Lyney or Grin-Malkin Hat
            return value
        # increase damage by 2
        assert mode == "REAL"
        self.usage -= 1
        value.damage += 2
        return value


class Lyney_4_3(CharacterBase):
    name: Literal["Lyney"]
    version: Literal["4.3"] = "4.3"
    element: ElementType = ElementType.PYRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase
        | PropArrow
        | ElementalSkillBase
        | WondrousTrickMiracleParade
    ] = []
    faction: List[FactionType] = [
        FactionType.FONTAINE,
        FactionType.FATUI,
        FactionType.ARKHE_PNEUMA,
    ]
    weapon_type: WeaponType = WeaponType.BOW

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name="Card Force Translocation",
                cost=PhysicalNormalAttackBase.get_cost(self.element),
            ),
            PropArrow(),
            ElementalSkillBase(
                name="Bewildering Lights",
                damage_type=DamageElementalType.PYRO,
                cost=ElementalSkillBase.get_cost(self.element),
            ),
            WondrousTrickMiracleParade(),
        ]


desc: Dict[str, DescDictType] = {
    "CHARACTER/Lyney": {
        "names": {"en-US": "Lyney", "zh-CN": "林尼"},
        "image_path": "cardface/Char_Avatar_Liney.png",  # noqa: E501
        "id": 1310,
        "descs": {"4.3": {"en-US": "", "zh-CN": ""}},
    },
    "SKILL_Lyney_NORMAL_ATTACK/Card Force Translocation": {
        "names": {"en-US": "Card Force Translocation", "zh-CN": "迫牌易位式"},
        "descs": {
            "4.3": {"en-US": "Deals 2 Physical DMG.", "zh-CN": "造成2点物理伤害。"}
        },
    },
    "SKILL_Lyney_NORMAL_ATTACK/Prop Arrow": {
        "names": {"en-US": "Prop Arrow", "zh-CN": "隐具魔术箭"},
        "descs": {
            "4.3": {
                "en-US": "Deals 2 Pyro DMG and summons Grin-Malkin Hat.\nHowever, if this character's HP is higher than the opposing active character's, they will gain 1 stack of Prop Surplus, and then take 1 Piercing DMG.",  # noqa: E501
                "zh-CN": "造成2点火元素伤害，召唤怪笑猫猫帽，累积1层隐具余数。\n如果本角色生命值至少为6，则对自身造成1点穿透伤害。",  # noqa: E501
            }
        },
    },
    "SUMMON/Grin-Malkin Hat": {
        "names": {"en-US": "Grin-Malkin Hat", "zh-CN": "怪笑猫猫帽"},
        "descs": {
            "4.3": {
                "en-US": "End Phase: Deal 1 Pyro DMG.\nUsage(s): 1 (Can stack. Max 2 stacks.)",  # noqa: E501
                "zh-CN": "结束阶段：造成1点火元素伤害。\n可用次数：1（可叠加，最多叠加到2次）",  # noqa: E501
            }
        },
        "image_path": "cardface/Summon_Liney.png",  # noqa: E501
    },
    "CHARACTER_STATUS/Prop Surplus": {
        "names": {"en-US": "Prop Surplus", "zh-CN": "隐具余数"},
        "descs": {
            "4.3": {
                "en-US": "Prop Surplus can stack up to 3 times.\nWhen this character uses Bewildering Lights: +1 DMG for each Prop Surplus stack. After the skill is finalized, consume all Prop Surplus, healing 1 HP for this character per stack.",  # noqa: E501
                "zh-CN": "隐具余数最多可以叠加到3层。\n角色使用眩惑光戏法时：每层隐具余数使伤害+1。技能结算后，耗尽隐具余数，每层治疗角色1点。",  # noqa: E501
            }
        },
    },
    "SKILL_Lyney_ELEMENTAL_SKILL/Bewildering Lights": {
        "names": {"en-US": "Bewildering Lights", "zh-CN": "眩惑光戏法"},
        "descs": {
            "4.3": {"en-US": "Deals 3 Pyro DMG.", "zh-CN": "造成3点火元素伤害。"}
        },
    },
    "SKILL_Lyney_ELEMENTAL_BURST/Wondrous Trick: Miracle Parade": {
        "names": {
            "en-US": "Wondrous Trick: Miracle Parade",
            "zh-CN": "大魔术·灵迹巡游",
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 3 Pyro DMG, summons 1 Grin-Malkin Hat, adds 1 stack of Prop Surplus.",  # noqa: E501
                "zh-CN": "造成3点火元素伤害，召唤怪笑猫猫帽，累积1层隐具余数。",  # noqa: E501
            }
        },
    },
    "TALENT_Lyney/Conclusive Ovation": {
        "names": {"en-US": "Conclusive Ovation", "zh-CN": "完场喝彩"},
        "descs": {
            "4.3": {
                "en-US": "Combat Action: When your active character is Lyney, equip this card.\nAfter Lyney equips this card, immediately use Prop Arrow.\nWhen Lyney is on the field and has this card equipped, the damage dealt by Lyney and your Grin-Malkin Hat will deal +1 DMG to characters affected by Pyro.\n(You must have Lyney in your deck to add this card to your deck.)",  # noqa: E501
                "zh-CN": "战斗行动：我方出战角色为林尼时，装备此牌。\n林尼装备此牌后，立刻使用一次隐具魔术箭。\n装备有此牌的林尼在场时，林尼自身和怪笑猫猫帽对具有火元素附着的角色造成的伤害+2。（每回合1次）\n（牌组中包含林尼，才能加入牌组）",  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Talent_Liney.png",  # noqa: E501
        "id": 213101,
    },
}


register_class(
    GrinMalkinHat_4_3 | PropSurplus_4_3 | ConclusiveOvation_4_3 | Lyney_4_3, desc
)
