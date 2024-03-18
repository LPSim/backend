from typing import Any, Dict, List, Literal

from pydantic import PrivateAttr

from lpsim.server.consts import IconType, SkillType
from lpsim.server.status.character_status.base import RoundEndAttackCharacterStatus
from lpsim.utils.class_registry import register_class
from lpsim.server.match import Match
from lpsim.utils.desc_registry import DescDictType
from lpsim.server.summon.base import AttackerSummonBase
from lpsim.server.modifiable_values import DamageValue
from lpsim.server.event import (
    RoundEndEventArguments,
    RoundPrepareEventArguments,
    SkillEndEventArguments,
)
from lpsim.server.action import (
    ActionTypes,
    Actions,
    ChangeObjectUsageAction,
    MakeDamageAction,
)
from lpsim.server.struct import Cost, ObjectPosition
from lpsim.consts import (
    ELEMENT_TO_DAMAGE_TYPE,
    DamageElementalType,
    DieColor,
    ElementType,
    FactionType,
    WeaponType,
)
from lpsim.server.character.character_base import (
    ElementalBurstBase,
    ElementalNormalAttackBase,
    ElementalSkillBase,
    CharacterBase,
    SkillTalent,
)


# Character status.


# Round status, will last for several rounds and disappear
class SnappySilhoete_4_5(RoundEndAttackCharacterStatus):
    name: Literal["Snappy Silhouette"] = "Snappy Silhouette"
    version: Literal["4.5"] = "4.5"
    usage: int = 2
    max_usage: int = 2
    icon_type: IconType = IconType.DEBUFF_ELEMENT_ICE
    damage: int = 1
    damage_elemental_type: DamageElementalType = DamageElementalType.CRYO

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        # when only 1 usage left, and self character has cryo app, increase damage to 2
        who: CharacterBase = self.query_one(match, "self")  # type: ignore
        assert who is not None
        if ElementType.CRYO in who.element_application and self.usage == 1:
            self.damage = 2
        return super().event_handler_ROUND_END(event, match)


# Summons


class NewsflashField_4_5(AttackerSummonBase):
    name: Literal["Newsflash Field"] = "Newsflash Field"
    version: Literal["4.5"] = "4.5"
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.CRYO
    damage: int = 1

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction | ChangeObjectUsageAction]:
        ret = super().event_handler_ROUND_END(event, match)
        damage_action = ret[0]
        assert damage_action.type == ActionTypes.MAKE_DAMAGE
        heal_targets = self.query(match, "our character is_alive=true")
        for target in heal_targets:
            damage_action.damage_value_list.append(
                DamageValue.create_heal(self.position, target.position, -1, Cost())
            )
        return ret


# Skills


class FramingFreezingPointComposition(ElementalSkillBase):
    name: Literal[
        "Framing: Freezing Point Composition"
    ] = "Framing: Freezing Point Composition"
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.CRYO
    cost: Cost = Cost(elemental_dice_color=DieColor.CRYO, elemental_dice_number=3)

    def get_actions(self, match: Match) -> List[Actions]:
        """
        Attack and create object
        """
        return super().get_actions(match) + [
            self.create_opposite_character_status(match, "Snappy Silhouette")
        ]


class StillPhotoComprehensiveConfirmation(ElementalBurstBase):
    name: Literal[
        "Still Photo: Comprehensive Confirmation"
    ] = "Still Photo: Comprehensive Confirmation"
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.CRYO
    cost: Cost = Cost(
        elemental_dice_color=DieColor.CRYO, elemental_dice_number=3, charge=2
    )

    def get_actions(self, match: Match) -> List[Actions]:
        ret: List[Actions] = super().get_actions(match)
        damage_action = ret[1]
        assert damage_action.type == ActionTypes.MAKE_DAMAGE
        characters = self.query(match, "our character is_alive=true")
        assert len(characters) > 0
        for character in characters:
            damage_action.damage_value_list.append(
                DamageValue.create_heal(
                    self.position, character.position, -1, self.cost
                )
            )
        ret.append(self.create_summon("Newsflash Field"))
        return ret


# Talents


class ASummationOfInterest_4_5(SkillTalent):
    name: Literal["A Summation of Interest"]
    version: Literal["4.5"] = "4.5"
    character_name: Literal["Charlotte"] = "Charlotte"
    cost: Cost = Cost(elemental_dice_color=DieColor.CRYO, elemental_dice_number=3)
    skill: Literal[
        "Framing: Freezing Point Composition"
    ] = "Framing: Freezing Point Composition"
    usage: int = 1
    _max_usage: int = PrivateAttr(1)

    def get_actions(self, target: ObjectPosition | None, match: Any) -> List[Actions]:
        self.usage = self._max_usage
        return super().get_actions(target, match)

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Match
    ) -> List[Actions]:
        self.usage = self._max_usage
        return []

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Match
    ) -> List[MakeDamageAction]:
        if self.usage <= 0:
            return []
        if self.position.not_satisfy(
            "source area=character and both pidx=same and target area=skill",
            target=event.action.position,
            match=match,
        ):
            # not equip, or not self use skill
            return []
        if event.action.skill_type != SkillType.NORMAL_ATTACK:
            # not normal attack
            return []
        target_status = self.query_one(
            match, 'opponent character status name="Snappy Silhouette"'
        )
        if target_status is None:
            # no target status
            return []
        self.usage -= 1
        target = self.query_one(match, "our active")
        assert target is not None
        return [
            MakeDamageAction(
                damage_value_list=[
                    DamageValue.create_heal(self.position, target.position, -2, Cost())
                ]
            )
        ]


# character base


# character class name should contain its version.
class Charlotte_4_5(CharacterBase):
    name: Literal["Charlotte"]
    version: Literal["4.5"] = "4.5"
    element: ElementType = ElementType.CRYO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        ElementalNormalAttackBase
        | FramingFreezingPointComposition
        | StillPhotoComprehensiveConfirmation
    ] = []
    faction: List[FactionType] = [FactionType.FONTAINE, FactionType.ARKHE_PNEUMA]
    weapon_type: WeaponType = WeaponType.CATALYST

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name="Cool-Color Capture",
                damage_type=ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost=ElementalNormalAttackBase.get_cost(self.element),
            ),
            FramingFreezingPointComposition(),
            StillPhotoComprehensiveConfirmation(),
        ]


# define descriptions of newly defined classes. Note key of skills and talents
# have character names. For balance changes, only descs are needed to define.
character_descs: Dict[str, DescDictType] = {
    "CHARACTER/Charlotte": {
        "names": {"en-US": "Charlotte", "zh-CN": "夏洛蒂"},
        "descs": {"4.5": {"en-US": "", "zh-CN": ""}},
        "image_path": "cardface/Char_Avatar_Charlotte.png",  # noqa: E501
        "id": 1110,
    },
    "SKILL_Charlotte_NORMAL_ATTACK/Cool-Color Capture": {
        "names": {"en-US": "Cool-Color Capture", "zh-CN": "冷色摄影律"},
        "descs": {
            "4.5": {"en-US": "Deals 1 Cryo DMG.", "zh-CN": "造成1点冰元素伤害。"}
        },
    },
    "SKILL_Charlotte_ELEMENTAL_SKILL/Framing: Freezing Point Composition": {
        "names": {
            "en-US": "Framing: Freezing Point Composition",
            "zh-CN": "取景·冰点构图法",
        },
        "descs": {
            "4.5": {
                "en-US": "Deals 1 Cryo DMG. Attach Snappy Silhouette to the target.",
                "zh-CN": "造成1点冰元素伤害，目标附属瞬时剪影。",
            }
        },
    },
    "CHARACTER_STATUS/Snappy Silhouette": {
        "names": {"en-US": "Snappy Silhouette", "zh-CN": "瞬时剪影"},
        "descs": {
            "4.5": {
                "en-US": "End Phase: Deal 1 Cryo DMG to the character(s) to which this is attached. If only 1 Usage(s) is remaining and the attached character is affected by Cryo, this instance of DMG +1.\nUsage(s): 2",  # noqa: E501
                "zh-CN": "结束阶段：对所附属角色造成1点冰元素伤害；如果可用次数仅剩余1且所附属角色具有冰元素附着，则此伤害+1。\n可用次数：2",  # noqa: E501
            }
        },
    },
    "SKILL_Charlotte_ELEMENTAL_BURST/Still Photo: Comprehensive Confirmation": {
        "names": {
            "en-US": "Still Photo: Comprehensive Confirmation",
            "zh-CN": "定格·全方位确证",
        },
        "descs": {
            "4.5": {
                "en-US": "Deals 1 Cryo DMG, heals all your characters for 1 HP, summons 1 Newsflash Field.",  # noqa: E501
                "zh-CN": "造成1点冰元素伤害，治疗我方所有角色1点，召唤临事场域。",
            }
        },
    },
    "SUMMON/Newsflash Field": {
        "names": {"en-US": "Newsflash Field", "zh-CN": "临事场域"},
        "descs": {
            "4.5": {
                "en-US": "End Phase: Deal 1 Cryo DMG, heal your active character for 1 HP.\nUsage(s): 2",  # noqa: E501
                "zh-CN": "结束阶段：造成1点冰元素伤害，治疗我方出战角色1点。\n可用次数：2",
            }
        },
        "image_path": "cardface/Summon_Charlotte.png",
    },
    "TALENT_Charlotte/A Summation of Interest": {
        "names": {"en-US": "A Summation of Interest", "zh-CN": "以有趣相关为要义"},
        "descs": {
            "4.5": {
                "en-US": "Combat Action: When your active character is Charlotte, equip this card.\nAfter Charlotte equips this card, immediately use Framing: Freezing Point Composition once.\nWhen your Charlotte, who has this card equipped, is on the field, and after any of your characters uses a Normal Attack: If your opponent has a character on the field with Snappy Silhouette attached, heal your active character for 2 HP. (Once per Round)\n(You must have Charlotte in your deck to add this card to your deck.)",  # noqa: E501
                "zh-CN": "战斗行动：我方出战角色为夏洛蒂时，装备此牌。\n夏洛蒂装备此牌后，立刻使用一次取景·冰点构图法。\n装备有此牌的夏洛蒂在场时，我方角色进行普通攻击后：如果对方场上有角色附属有瞬时剪影，则治疗我方出战角色2点。（每回合1次）\n（牌组中包含夏洛蒂，才能加入牌组）",  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Talent_Charlotte.png",  # noqa: E501
        "id": 211101,
    },
}


register_class(
    Charlotte_4_5 | SnappySilhoete_4_5 | NewsflashField_4_5 | ASummationOfInterest_4_5,
    character_descs,
)
