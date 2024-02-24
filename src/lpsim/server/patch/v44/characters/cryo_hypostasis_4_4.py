from typing import Any, Dict, List, Literal

from ....action import (
    ActionTypes,
    ChangeObjectUsageAction,
    MakeDamageAction,
    RemoveObjectAction,
)
from ....event import RemoveObjectEventArguments, RoundEndEventArguments
from ....match import Match
from ....status.character_status.base import ReviveCharacterStatus, UsageCharacterStatus
from .....utils.class_registry import register_class
from .....utils.desc_registry import DescDictType
from ....summon.base import AttackerSummonBase
from ....action import Actions, CreateObjectAction
from ....struct import Cost, ObjectPosition
from ....consts import (
    CostLabels,
    DamageElementalType,
    DieColor,
    ElementType,
    FactionType,
    IconType,
    ObjectPositionType,
    WeaponType,
)
from ....character.character_base import (
    AOESkillBase,
    CreateStatusPassiveSkill,
    ElementalBurstBase,
    ElementalNormalAttackBase,
    ElementalSkillBase,
    CharacterBase,
    TalentBase,
)


class OverwhelmingIce_4_4(UsageCharacterStatus):
    name: Literal["Overwhelming Ice"] = "Overwhelming Ice"
    version: Literal["4.4"] = "4.4"
    usage: int = 1
    max_usage: int = 1
    icon_type: IconType = IconType.ATK_SELF


class CryocrystalCore_4_4(ReviveCharacterStatus):
    name: Literal["Cryocrystal Core"] = "Cryocrystal Core"
    version: Literal["4.4"] = "4.4"
    heal: int = 1


class PiercingIceridge_4_4(AttackerSummonBase):
    name: Literal["Piercing Iceridge"] = "Piercing Iceridge"
    version: Literal["4.4"] = "4.4"
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.CRYO
    damage: int = 1

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Match
    ) -> List[MakeDamageAction | ChangeObjectUsageAction]:
        ret = super().event_handler_ROUND_END(event, match)
        damage_action = ret[0]
        assert damage_action.type == ActionTypes.MAKE_DAMAGE
        # get closest character
        our_active = match.player_tables[self.position.player_idx].active_character_idx
        target_characters = match.player_tables[1 - self.position.player_idx].characters
        target_idx = our_active
        if target_characters[target_idx].is_defeated:
            # need to choose another character
            for idx, character in enumerate(target_characters):
                if not character.is_defeated:
                    target_idx = idx
                    break
            else:
                raise AssertionError("No character alive")
        damage_action.damage_value_list[0].target_position = target_characters[
            target_idx
        ].position
        return ret


# Skills


class IcespikeShot(ElementalNormalAttackBase, AOESkillBase):
    name: Literal["Icespike Shot"] = "Icespike Shot"
    version: Literal["4.4"] = "4.4"
    damage: int = 1
    back_damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.CRYO
    cost: Cost = Cost(
        elemental_dice_color=DieColor.CRYO, elemental_dice_number=1, any_dice_number=2
    )

    def get_actions(self, match: Match) -> List[Actions]:
        found_target = self.query_one(match, "self status 'name=Overwhelming Ice'")
        if found_target is not None:
            # use AOE attack opposite
            return [
                self.attack_opposite_active(match, self.damage, self.damage_type),
                self.charge_self(1),
                RemoveObjectAction(object_position=found_target.position),
            ]
        # use normal attack opposite
        return [
            ElementalNormalAttackBase.attack_opposite_active(
                self, match, self.damage, self.damage_type
            ),
            self.charge_self(1),
        ]


class IceRingWaltz(ElementalSkillBase):
    name: Literal["Ice Ring Waltz"] = "Ice Ring Waltz"
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.CRYO
    cost: Cost = Cost(elemental_dice_color=DieColor.CRYO, elemental_dice_number=3)

    def get_actions(self, match: Match) -> List[Actions]:
        """
        Attack and create object
        """
        return super().get_actions(match) + [
            self.create_character_status("Overwhelming Ice"),
        ]


class PlungingIceShards(ElementalBurstBase, AOESkillBase):
    name: Literal["Plunging Ice Shards"] = "Plunging Ice Shards"
    damage: int = 2
    back_damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.CRYO
    cost: Cost = Cost(
        elemental_dice_color=DieColor.CRYO,
        elemental_dice_number=3,
        charge=2,
    )

    def get_actions(self, match: Match) -> List[Actions]:
        return super().get_actions(match) + [self.create_summon("Piercing Iceridge")]


class CryocrystalCore(CreateStatusPassiveSkill):
    name: Literal["Cryocrystal Core"] = "Cryocrystal Core"
    status_name: Literal["Cryocrystal Core"] = "Cryocrystal Core"
    regenerate_when_revive: bool = False


# Talents


class SternfrostPrism_4_4(TalentBase):
    name: Literal["Sternfrost Prism"]
    version: Literal["4.4"] = "4.4"
    character_name: Literal["Cryo Hypostasis"] = "Cryo Hypostasis"
    cost: Cost = Cost(
        elemental_dice_color=DieColor.CRYO,
        elemental_dice_number=1,
    )
    cost_label: int = (
        CostLabels.CARD.value | CostLabels.TALENT.value | CostLabels.EQUIPMENT.value
    )
    remove_when_used: bool = False

    def get_actions(self, target: ObjectPosition | None, match: Match) -> List[Actions]:
        """
        Using this card will attach cryo crystal core to it.
        """
        ret = super().get_actions(target, match)
        character: Any = self.query_one(match, "our active")
        assert character is not None and character.name == self.character_name
        return ret + [
            CreateObjectAction(
                object_name="Cryocrystal Core",
                object_position=character.position.set_area(
                    ObjectPositionType.CHARACTER_STATUS
                ),
                object_arguments={},
            )
        ]

    def event_handler_REMOVE_OBJECT(
        self, event: RemoveObjectEventArguments, match: Match
    ) -> List[CreateObjectAction]:
        """
        When this card equipped, cryo core is removed from self, create
        sheer cold on opposite active.
        """
        if self.position.not_satisfy(
            "both pidx=same cidx=same "
            "and source area=character "
            "and target area=character_status",
            event.action.object_position,
        ):
            # not equipped, or target not self character status
            return []
        if event.object_name != "Cryocrystal Core":
            # not cryo crystal core
            return []
        target = match.player_tables[
            1 - self.position.player_idx
        ].get_active_character()
        return [
            CreateObjectAction(
                object_position=target.position.set_area(
                    ObjectPositionType.CHARACTER_STATUS
                ),
                object_name="Sheer Cold",
                object_arguments={},
            )
        ]


class CryoHypostasis_4_4(CharacterBase):
    name: Literal["Cryo Hypostasis"]
    version: Literal["4.4"] = "4.4"
    element: ElementType = ElementType.CRYO
    max_hp: int = 8
    max_charge: int = 2
    skills: List[IcespikeShot | IceRingWaltz | PlungingIceShards | CryocrystalCore] = []
    faction: List[FactionType] = [FactionType.MONSTER]
    weapon_type: WeaponType = WeaponType.OTHER

    def _init_skills(self) -> None:
        self.skills = [
            IcespikeShot(),
            IceRingWaltz(),
            PlungingIceShards(),
            CryocrystalCore(),
        ]


# define descriptions of newly defined classes. Note key of skills and talents
# have character names. For balance changes, only descs are needed to define.
character_descs: Dict[str, DescDictType] = {
    "CHARACTER/Cryo Hypostasis": {
        "names": {"en-US": "Cryo Hypostasis", "zh-CN": "无相之冰"},
        "descs": {"4.4": {"en-US": "", "zh-CN": ""}},
        "image_path": "cardface/Char_Monster_EffigyIce.png",  # noqa: E501
        "id": 2103,
    },
    "SKILL_Cryo Hypostasis_NORMAL_ATTACK/Icespike Shot": {
        "names": {"en-US": "Icespike Shot", "zh-CN": "冰锥迸射"},
        "descs": {
            "4.4": {"en-US": "Deals 1 Cryo DMG.", "zh-CN": "造成1点冰元素伤害。"}
        },
    },
    "SKILL_Cryo Hypostasis_ELEMENTAL_SKILL/Ice Ring Waltz": {
        "names": {"en-US": "Ice Ring Waltz", "zh-CN": "圆舞冰环"},
        "descs": {
            "4.4": {
                "en-US": "Deals 3 Cryo DMG. This character gains Overwhelming Ice.",  # noqa: E501
                "zh-CN": "造成3点冰元素伤害，本角色附属四迸冰锥。",
            }
        },
    },
    "CHARACTER_STATUS/Overwhelming Ice": {
        "names": {"en-US": "Overwhelming Ice", "zh-CN": "四迸冰锥"},
        "descs": {
            "4.4": {
                "en-US": "When the character uses a Normal Attack: Deal 1 Piercing DMG to all opposing characters on standby. .\nUsage(s): 1",  # noqa: E501
                "zh-CN": "角色进行普通攻击时：对所有敌方后台角色造成1点穿透伤害。\n可用次数：1",  # noqa: E501
            }
        },
    },
    "SKILL_Cryo Hypostasis_ELEMENTAL_BURST/Plunging Ice Shards": {
        "names": {"en-US": "Plunging Ice Shards", "zh-CN": "冰棱轰坠"},
        "descs": {
            "4.4": {
                "en-US": "Deals 2 Cryo DMG, deals 1 Piercing DMG to all opposing characters on standby, summons 1 Piercing Iceridge.",  # noqa: E501
                "zh-CN": "造成2点冰元素伤害，对所有敌方后台角色造成1点穿透伤害，召唤刺击冰棱。",  # noqa: E501
            }
        },
    },
    "SUMMON/Piercing Iceridge": {
        "names": {"en-US": "Piercing Iceridge", "zh-CN": "刺击冰棱"},
        "descs": {
            "4.4": {
                "en-US": "End Phase: Deal 1 Cryo DMG to the opposing Character Closest to Your Current Active Character.\nUsage(s): 2",  # noqa: E501
                "zh-CN": "结束阶段：对敌方距离我方出战角色最近的角色造成1点冰元素伤害。\n可用次数：2",  # noqa: E501
            }
        },
        "image_path": "cardface/Summon_EffigyIce.png",
    },
    "SKILL_Cryo Hypostasis_PASSIVE/Cryocrystal Core": {
        "names": {"en-US": "Cryocrystal Core", "zh-CN": "冰晶核心"},
        "descs": {
            "4.4": {
                "en-US": "(Passive) When the battle begins, this character gains Cryocrystal Core.",  # noqa: E501
                "zh-CN": "【被动】战斗开始时，初始附属冰晶核心。",
            }
        },
    },
    "CHARACTER_STATUS/Cryocrystal Core": {
        "names": {"en-US": "Cryocrystal Core", "zh-CN": "冰晶核心"},
        "descs": {
            "4.4": {
                "en-US": "When the character to which this is attached would be defeated: Remove this effect, ensure the character $[K54|s1], and heal them to 1 HP.",  # noqa: E501
                "zh-CN": "所附属角色被击倒时：移除此效果，使角色免于被击倒，并治疗该角色到1点生命值。",  # noqa: E501
            }
        },
    },
    "TALENT_Cryo Hypostasis/Sternfrost Prism": {
        "names": {"en-US": "Sternfrost Prism", "zh-CN": "严霜棱晶"},
        "descs": {
            "4.4": {
                "en-US": "Can only be played if your active character is Cryo Hypostasis: Attach Cryocrystal Core to them.\nAfter Cryo Hypostasis, who has this card equipped, triggers Cryocrystal Core: Attach Sheer Cold to the opposing active character.\n(Your deck must contain Cryo Hypostasis to add this card to your deck)",  # noqa: E501
                "zh-CN": "我方出战角色为无相之冰时，才能打出：使其附属冰晶核心。\n装备有此牌的无相之冰触发冰晶核心后：对敌方出战角色附属严寒。\n（牌组中包含无相之冰，才能加入牌组）",  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Talent_EffigyIce.png",  # noqa: E501
        "id": 221031,
    },
}


register_class(
    CryoHypostasis_4_4
    | OverwhelmingIce_4_4
    | CryocrystalCore_4_4
    | PiercingIceridge_4_4
    | SternfrostPrism_4_4,
    character_descs,
)
