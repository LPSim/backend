from typing import Any, Dict, List, Literal

from ....action import Actions, CreateDiceAction, CreateObjectAction, RemoveObjectAction
from .....utils.class_registry import register_class
from ....status.character_status.base import (
    DefendCharacterStatus,
    ReviveCharacterStatus,
    RoundEndAttackCharacterStatus,
)
from .....utils import BaseModel
from ....event import (
    CreateObjectEventArguments,
    MakeDamageEventArguments,
    PlayerActionStartEventArguments,
    RemoveObjectEventArguments,
    RoundPrepareEventArguments,
)
from ....match import Match
from ....struct import Cost, ObjectPosition
from ....consts import (
    DAMAGE_TYPE_TO_ELEMENT,
    ELEMENT_TO_DIE_COLOR,
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
    CharacterBase,
    CreateStatusPassiveSkill,
    ElementalBurstBase,
    ElementalNormalAttackBase,
    ElementalSkillBase,
    TalentBase,
)
from .....utils.desc_registry import DescDictType


class PainForPainStatus_4_3(DefendCharacterStatus):
    name: Literal["Pain for Pain"] = "Pain for Pain"
    version: Literal["4.3"] = "4.3"
    usage: int = 1
    max_usage: int = 1
    min_damage_to_trigger: int = 3
    max_in_one_time: int = 1

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Match
    ) -> List[RemoveObjectAction | CreateObjectAction]:
        """
        After make damage, if self usage becomes 0 (which means it negates
        DMG), super will remove self. At this time, create status for opposite
        active character.
        """
        ret: List[RemoveObjectAction | CreateObjectAction] = []
        ret += super().event_handler_MAKE_DAMAGE(event, match)
        if len(ret) == 0:
            # not remove self, do nothing
            return ret
        target = match.player_tables[
            1 - self.position.player_idx
        ].get_active_character()
        our = match.player_tables[self.position.player_idx].characters[
            self.position.character_idx
        ]
        assert our.name == "Signora"
        if our.element == ElementType.CRYO:
            status_name = "Sheer Cold"
        elif our.element == ElementType.PYRO:
            status_name = "Blazing Heat"
        else:
            raise AssertionError(f"Unknown element {our.element}")
        ret.append(
            CreateObjectAction(
                object_position=target.position.set_area(
                    ObjectPositionType.CHARACTER_STATUS
                ),
                object_name=status_name,
                object_arguments={},
            )
        )
        return ret


class IceSealedCrimsonWitchOfEmbers_4_3(ReviveCharacterStatus):
    name: Literal[
        "Ice-Sealed Crimson Witch of Embers"
    ] = "Ice-Sealed Crimson Witch of Embers"
    version: Literal["4.3"] = "4.3"
    heal: int = 1
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

    def event_handler_ROUND_PREPARE(
        self, event: PlayerActionStartEventArguments, match: Match
    ) -> List[RemoveObjectAction]:
        character = match.player_tables[self.position.player_idx].characters[
            self.position.character_idx
        ]
        if character.hp > 4:
            # hp > 4, not remove
            return []
        # hp <= 4, remove
        return [RemoveObjectAction(object_position=self.position)]


class SheerCold_4_3(RoundEndAttackCharacterStatus):
    name: Literal[
        "Sheer Cold",
        "Blazing Heat",
    ]
    version: Literal["4.3"] = "4.3"
    usage: int = 1
    max_usage: int = 1
    damage: int = 1

    # will modify when init
    damage_elemental_type: DamageElementalType = DamageElementalType.PIERCING
    icon_type: Literal[
        IconType.DEBUFF_ELEMENT_ICE, IconType.DEBUFF_ELEMENT_FIRE
    ] = IconType.DEBUFF_ELEMENT_ICE

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        if self.name == "Sheer Cold":
            self.damage_elemental_type = DamageElementalType.CRYO
            self.icon_type = IconType.DEBUFF_ELEMENT_ICE
        elif self.name == "Blazing Heat":
            self.damage_elemental_type = DamageElementalType.PYRO
            self.icon_type = IconType.DEBUFF_ELEMENT_FIRE
        else:
            raise AssertionError(f"Unknown name {self.name}")

    def event_handler_CREATE_OBJECT(
        self, event: CreateObjectEventArguments, match: Match
    ) -> List[RemoveObjectAction]:
        """
        When a character attaches two status, remove status in previous.
        This will only perform on Blazing Heat to avoid generating multiple
        RemoveObjectAction for same status.
        """
        if self.name != "Blazing Heat":
            # not Blazing Heat, do nothing
            return []
        status = (
            match.player_tables[self.position.player_idx]
            .characters[self.position.character_idx]
            .status
        )
        blazing_heat = None
        sheer_cold = None
        for sidx, s in enumerate(status):
            if s.name == "Blazing Heat":
                blazing_heat = [sidx, s]
            elif s.name == "Sheer Cold":
                sheer_cold = [sidx, s]
        assert blazing_heat is not None
        if sheer_cold is None:
            # no sheer cold, do nothing
            return []
        # remove status in previous
        assert blazing_heat[0] != sheer_cold[0]
        if blazing_heat[0] < sheer_cold[0]:
            target = blazing_heat[1]
        else:
            target = sheer_cold[1]
        return [
            RemoveObjectAction(object_position=target.position),
        ]


class SignoraSkillValidCheck(BaseModel):
    """
    Used in all Signora's skills to check if skill is valid.
    """

    position: ObjectPosition = ObjectPosition(
        player_idx=-1,
        area=ObjectPositionType.INVALID,
        id=-1,
    )
    damage_type: DamageElementalType

    def is_valid(self, match: Match) -> bool:
        character = match.player_tables[self.position.player_idx].characters[
            self.position.character_idx
        ]
        assert character.name == "Signora"
        return (character.desc == "") == (self.damage_type == DamageElementalType.CRYO)


class SignoraNormalAttack(SignoraSkillValidCheck, ElementalNormalAttackBase):
    """
    availability based on Signora's desc.
    """

    name: Literal[
        "Frostblade Hailstorm",
        "Fire Normal Attack",
    ]

    # will modify when init
    damage_type: DamageElementalType = DamageElementalType.PIERCING
    cost: Cost = Cost()

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        if self.name == "Frostblade Hailstorm":
            self.damage_type = DamageElementalType.CRYO
        elif self.name == "Fire Normal Attack":
            self.damage_type = DamageElementalType.PYRO
        else:
            raise AssertionError(f"Unknown name {self.name}")
        self.cost = Cost(
            elemental_dice_color=ELEMENT_TO_DIE_COLOR[
                DAMAGE_TYPE_TO_ELEMENT[self.damage_type]
            ],
            elemental_dice_number=1,
            any_dice_number=2,
        )


class SignoraElementalSkill(SignoraSkillValidCheck, ElementalSkillBase):
    """
    availability based on Signora's desc.
    """

    name: Literal[
        "Biting Shards",
        "Fire Elemental Skill",
    ]

    # will modify when init
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.PIERCING
    cost: Cost = Cost(elemental_dice_number=3)

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        if self.name == "Biting Shards":
            self.damage_type = DamageElementalType.CRYO
        elif self.name == "Fire Elemental Skill":
            self.damage_type = DamageElementalType.PYRO
        else:
            raise AssertionError(f"Unknown name {self.name}")
        self.cost.elemental_dice_color = ELEMENT_TO_DIE_COLOR[
            DAMAGE_TYPE_TO_ELEMENT[self.damage_type]
        ]

    def get_actions(self, match: Match) -> List[Actions]:
        if self.damage_type == DamageElementalType.CRYO:
            status_name = "Sheer Cold"
        elif self.damage_type == DamageElementalType.PYRO:
            status_name = "Blazing Heat"
        else:
            raise AssertionError(f"Unknown damage type {self.damage_type}")
        return super().get_actions(match) + [
            self.create_opposite_character_status(match, status_name)
        ]


class CarmineChrysalis(SignoraSkillValidCheck, ElementalBurstBase):
    name: Literal["Carmine Chrysalis"] = "Carmine Chrysalis"
    damage: int = 4
    damage_type: DamageElementalType = DamageElementalType.CRYO
    cost: Cost = Cost(
        elemental_dice_color=DieColor.CRYO, elemental_dice_number=3, charge=2
    )

    def get_actions(self, match: Match) -> List[Actions]:
        """
        Damage 4, heal 2, and remove status.
        """
        damage = self.attack_opposite_active(match, self.damage, self.damage_type)
        heal = self.attack_self(match, -2)
        damage.damage_value_list += heal.damage_value_list
        status_list = (
            match.player_tables[self.position.player_idx]
            .characters[self.position.character_idx]
            .status
        )
        target_status = None
        for s in status_list:
            if s.name == "Ice-Sealed Crimson Witch of Embers":  # pragma: no branch
                target_status = s
                break
        else:
            raise AssertionError("Cannot find status")
        return [
            self.charge_self(-2),
            damage,
            RemoveObjectAction(object_position=target_status.position),
        ]


class SignoraPyroBurst(SignoraSkillValidCheck, ElementalBurstBase):
    name: Literal["Pyro Burst"] = "Pyro Burst"
    damage: int = 6
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = Cost(
        elemental_dice_color=DieColor.PYRO, elemental_dice_number=3, charge=2
    )


class MightOfDelusion(CreateStatusPassiveSkill):
    name: Literal["Might of Delusion"] = "Might of Delusion"
    status_name: Literal[
        "Ice-Sealed Crimson Witch of Embers"
    ] = "Ice-Sealed Crimson Witch of Embers"
    regenerate_when_revive: bool = False


class PainForPain_4_3(TalentBase):
    name: Literal["Pain for Pain"]
    version: Literal["4.3"] = "4.3"
    character_name: Literal["Signora"] = "Signora"
    cost_label: int = (
        CostLabels.CARD.value | CostLabels.TALENT.value | CostLabels.EQUIPMENT.value
    )
    cost: Cost = Cost(same_dice_number=3)

    def equip(self, match: Any) -> List[CreateDiceAction | CreateObjectAction]:
        """
        When equip, generate 3 element dice and create status.
        """
        character = match.player_tables[self.position.player_idx].characters[
            self.position.character_idx
        ]
        assert character.name == self.character_name
        return [
            CreateDiceAction(
                player_idx=self.position.player_idx,
                number=3,
                color=ELEMENT_TO_DIE_COLOR[character.element],
            ),
            CreateObjectAction(
                object_name=self.name,
                object_position=self.position.set_area(
                    ObjectPositionType.CHARACTER_STATUS
                ),
                object_arguments={},
            ),
        ]

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Match
    ) -> List[CreateObjectAction]:
        """
        When round prepare and equipped, create status.
        """
        if self.position.area != ObjectPositionType.CHARACTER:
            # not equipped, do nothing
            return []
        return [
            CreateObjectAction(
                object_name=self.name,
                object_position=self.position.set_area(
                    ObjectPositionType.CHARACTER_STATUS
                ),
                object_arguments={},
            )
        ]


class Signora_4_3(CharacterBase):
    name: Literal["Signora"]
    version: Literal["4.3"] = "4.3"
    desc: Literal["", "pyro"] = ""
    element: ElementType = ElementType.CRYO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        SignoraNormalAttack
        | SignoraElementalSkill
        | CarmineChrysalis
        | SignoraPyroBurst
        | MightOfDelusion
    ] = []
    faction: List[FactionType] = [FactionType.FATUI]
    weapon_type: WeaponType = WeaponType.OTHER

    def _init_skills(self) -> None:
        self.skills = [
            SignoraNormalAttack(name="Frostblade Hailstorm"),
            SignoraNormalAttack(name="Fire Normal Attack"),
            SignoraElementalSkill(name="Biting Shards"),
            SignoraElementalSkill(name="Fire Elemental Skill"),
            CarmineChrysalis(),
            SignoraPyroBurst(),
            MightOfDelusion(),
        ]

    def event_handler_REMOVE_OBJECT(
        self, event: RemoveObjectEventArguments, match: Match
    ) -> List[Actions]:
        """
        When Ice-Sealed Crimson Witch of Embers is removed, transform self
        element and desc.
        """
        status = (
            match.player_tables[self.position.player_idx]
            .characters[self.position.character_idx]
            .status
        )
        for s in status:
            if (  # pragma: no branch
                s.name == "Ice-Sealed Crimson Witch of Embers"
            ):
                # status still valid, do nothing
                return []
        # status not found, transform
        self.element = ElementType.PYRO
        self.desc = "pyro"
        return []


desc: Dict[str, DescDictType] = {
    "CHARACTER/Signora": {
        "names": {"en-US": "Signora", "zh-CN": "「女士」"},
        "descs": {"4.3": {"en-US": "", "zh-CN": ""}},
        "image_path": "cardface/Char_Monster_LaSignora.png",  # noqa: E501
        "id": 2102,
    },
    "CHARACTER/Signora_pyro": {
        "names": {"en-US": "Signora·Burned", "zh-CN": "「女士」·燃起来了"},
        "descs": {"4.3": {"en-US": "", "zh-CN": ""}},
        "image_path": "cardface/Char_Monster_LaSignoraHarbinger.png",  # noqa: E501
    },
    "SKILL_Signora_NORMAL_ATTACK/Frostblade Hailstorm": {
        "names": {"en-US": "Frostblade Hailstorm", "zh-CN": "霜锋霰舞"},
        "descs": {
            "4.3": {"en-US": "Deals 1 Cryo DMG.", "zh-CN": "造成1点冰元素伤害。"}
        },
    },
    "SKILL_Signora_NORMAL_ATTACK/Fire Normal Attack": {
        "names": {"en-US": "Crimson Lotus Moth", "zh-CN": "红莲之蛾"},
        "descs": {
            "4.3": {"en-US": "Deals 1 Pyro DMG.", "zh-CN": "造成1点火元素伤害。"}
        },
    },
    "SKILL_Signora_ELEMENTAL_SKILL/Biting Shards": {
        "names": {"en-US": "Biting Shards", "zh-CN": "凛冽之刺"},
        "descs": {
            "4.3": {
                "en-US": "Deals 2 Cryo DMG. The target character receives Sheer Cold.",  # noqa: E501
                "zh-CN": "造成2点冰元素伤害，目标角色附属严寒。",
            }
        },
    },
    "SKILL_Signora_ELEMENTAL_SKILL/Fire Elemental Skill": {
        "names": {"en-US": "Decimating Lash", "zh-CN": "烬灭之鞭"},
        "descs": {
            "4.3": {
                "en-US": "Deals 2 Pyro DMG. The target character receives Blazing Heat.",  # noqa: E501
                "zh-CN": "造成2点火元素伤害，目标角色附属炽热。",
            }
        },
    },
    "CHARACTER_STATUS/Sheer Cold": {
        "names": {"en-US": "Sheer Cold", "zh-CN": "严寒"},
        "descs": {
            "4.3": {
                "en-US": "End Phase: Deals 1 Cryo DMG to attached character.\nUsage(s): 1\n\nWhen attached character has Blazing Heat attached, remove this effect.",  # noqa: E501
                "zh-CN": "结束阶段：对附属角色造成1点冰元素伤害。\n可用次数：1\n\n所附属角色被附属炽热时，移除此效果。",  # noqa: E501
            }
        },
    },
    "CHARACTER_STATUS/Blazing Heat": {
        "names": {"en-US": "Blazing Heat", "zh-CN": "炽热"},
        "descs": {
            "4.3": {
                "en-US": "End Phase: Deals 1 Pyro DMG to attached character.\nUsage(s): 1\n\nWhen attached character has Sheer Cold attached, remove this effect.",  # noqa: E501
                "zh-CN": "结束阶段：对附属角色造成1点火元素伤害。\n可用次数：1\n\n所附属角色被附属严寒时，移除此效果。",  # noqa: E501
            }
        },
    },
    "SKILL_Signora_ELEMENTAL_BURST/Carmine Chrysalis": {
        "names": {"en-US": "Carmine Chrysalis", "zh-CN": "红莲冰茧"},
        "descs": {
            "4.3": {
                "en-US": "Deals 4 Cryo DMG, heals this character for 2 HP. Removes Ice-Sealed Crimson Witch of Embers. This character permanently switches to Crimson Witch of Embers state.",  # noqa: E501
                "zh-CN": "造成4点冰元素伤害，治疗本角色2点。移除冰封的炽炎魔女，本角色永久转换为「焚尽的炽炎魔女」形态。",  # noqa: E501
            }
        },
    },
    "SKILL_Signora_ELEMENTAL_BURST/Pyro Burst": {
        "names": {"en-US": "Whirling Blaze", "zh-CN": "燃焰旋织"},
        "descs": {
            "4.3": {"en-US": "Deals 6 Pyro DMG.", "zh-CN": "造成6点火元素伤害。"}
        },
    },
    "CHARACTER_STATUS/Ice-Sealed Crimson Witch of Embers": {
        "names": {
            "en-US": "Ice-Sealed Crimson Witch of Embers",
            "zh-CN": "冰封的炽炎魔女",
        },
        "descs": {
            "4.3": {
                "en-US": "When the Action Phase starts: If the attached character has no more than 4 HP, remove this effect.\nWhen attached character is defeated: Remove this effect, ensure that character $[K54|s1] and heal them to 1 HP.\n\nWhen this effect is removed: Attached character will transform into the Crimson Witch of Embers state.",  # noqa: E501
                "zh-CN": "行动阶段开始时：如果所附属角色生命值不多于4，则移除此效果。\n所附属角色被击倒时：移除此效果，使角色免于被击倒，并治疗该角色到1点生命值。\n\n此效果被移除时：所附属角色转换为「焚尽的炽炎魔女」形态。",  # noqa: E501
            }
        },
        "image_path": "status/LaSignora_S.png",
    },
    "SKILL_Signora_PASSIVE/Might of Delusion": {
        "names": {"en-US": "Might of Delusion", "zh-CN": "邪眼之威"},
        "descs": {
            "4.3": {
                "en-US": "(Passive) When the battle begins, this character gains Ice-Sealed Crimson Witch of Embers.",  # noqa: E501
                "zh-CN": "【被动】战斗开始时，初始附属冰封的炽炎魔女。",
            }
        },
    },
    "CHARACTER_STATUS/Pain for Pain": {
        "names": {"en-US": "Pain for Pain", "zh-CN": "苦痛奉还"},
        "descs": {
            "4.3": {
                "en-US": "When this character takes at least 3 DMG: Negates 1 DMG, then apply Sheer Cold or Blazing Heat to the opposing active character based on Signora's state. (Once per Round)",  # noqa: E501
                "zh-CN": "角色受到至少为3点的伤害时：抵消1点伤害，然后根据「女士」的形态对敌方出战角色附属严寒或炽热。（每回合1次）",  # noqa: E501
            }
        },
    },
    "TALENT_Signora/Pain for Pain": {
        "names": {"en-US": "Pain for Pain", "zh-CN": "苦痛奉还"},
        "descs": {
            "4.3": {
                "en-US": "Can only be played if your active character is Signora: When entering play, generate 3 Elemental Dice of the same Type as Signora.\nWhen this character takes at least 3 DMG: Negates 1 DMG, then apply Sheer Cold or Blazing Heat to the opposing active character based on Signora's state. (Once per Round)\n(Your deck must contain Signora to add this card to your deck)",  # noqa: E501
                "zh-CN": "我方出战角色为「女士」时，才能打出：入场时，生成3个「女士」当前元素类型的元素骰。\n角色受到至少为3点的伤害时：抵消1点伤害，然后根据「女士」的形态对敌方出战角色附属严寒或炽热。（每回合1次）\n（牌组中包含「女士」，才能加入牌组）",  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Talent_LaSignora.png",  # noqa: E501
        "id": 221021,
    },
}


register_class(
    IceSealedCrimsonWitchOfEmbers_4_3
    | SheerCold_4_3
    | Signora_4_3
    | PainForPain_4_3
    | PainForPainStatus_4_3,
    desc,
)
