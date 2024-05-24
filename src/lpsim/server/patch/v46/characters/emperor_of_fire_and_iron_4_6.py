from typing import List, Literal
from lpsim.server.action import (
    Actions,
    ChangeObjectUsageAction,
    CreateObjectAction,
    MakeDamageAction,
    RemoveObjectAction,
)
from lpsim.server.character.character_base import (
    AOESkillBase,
    CharacterBase,
    CreateStatusPassiveSkill,
    ElementalBurstBase,
    ElementalSkillBase,
    PhysicalNormalAttackBase,
    TalentBase,
)
from lpsim.server.consts import (
    DamageElementalType,
    DieColor,
    ElementType,
    FactionType,
    IconType,
    ObjectPositionType,
    WeaponType,
)
from lpsim.server.event import ActionEndEventArguments, RoundPrepareEventArguments
from lpsim.server.match import Match
from lpsim.server.modifiable_values import DamageValue
from lpsim.server.status.base import StatusBase
from lpsim.server.status.character_status.base import (
    CharacterStatusBase,
    PrepareCharacterStatus,
    ShieldCharacterStatus,
)
from lpsim.server.struct import Cost, ObjectPosition
from lpsim.utils.class_registry import register_class
from lpsim.utils.desc_registry import DescDictType


# Skills


class ArmoredCrabCarapace_4_6(ShieldCharacterStatus):
    name: Literal["Armored Crab Carapace"] = "Armored Crab Carapace"
    version: Literal["4.6"] = "4.6"
    icon_type: IconType = IconType.SHIELD
    usage: int = 5  # initial usage
    max_usage: int = 999


class SearingBlast_4_6(PrepareCharacterStatus):
    name: Literal["Searing Blast"] = "Searing Blast"
    version: Literal["4.6"] = "4.6"
    character_name: Literal["Emperor of Fire and Iron"] = "Emperor of Fire and Iron"
    skill_name: Literal["Searing Blast"] = "Searing Blast"


class BusterBlaze(ElementalSkillBase):
    name: Literal["Buster Blaze"] = "Buster Blaze"
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = Cost(elemental_dice_color=DieColor.PYRO, elemental_dice_number=3)

    def get_actions(self, match: Match) -> list[Actions]:
        armor = self.query_one(match, 'self status name="Armored Crab Carapace"')
        if armor is not None and armor.usage >= 7:  # type: ignore
            self.damage += 1
            ret = super().get_actions(match)
            self.damage -= 1
        else:
            ret = super().get_actions(match)
        return ret + [
            self.create_character_status("Armored Crab Carapace", {"usage": 2}),
        ]


class BattleLineDetonation(ElementalBurstBase):
    name: Literal["Battle-Line Detonation"] = "Battle-Line Detonation"
    damage: int = 0
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = Cost(
        elemental_dice_color=DieColor.PYRO, elemental_dice_number=3, charge=2
    )

    def get_actions(self, match: Match) -> list[Actions]:
        return [self.charge_self(-2), self.create_character_status("Searing Blast")]


class SearingBlast(ElementalBurstBase, AOESkillBase):
    name: Literal["Searing Blast"] = "Searing Blast"
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.PYRO
    back_damage: int = 2
    cost: Cost = Cost()

    def is_valid(self, match: Match):
        return False

    def get_actions(self, match: Match) -> list[Actions]:
        armor: CharacterStatusBase | None = self.query_one(
            match, 'self status name="Armored Crab Carapace"'
        )  # type: ignore
        if armor is not None:
            self.damage += armor.usage // 2
            ret = super().get_actions(match)
            self.damage -= armor.usage // 2
        else:
            ret = super().get_actions(match)
        return ret


class ImperialPanoply(CreateStatusPassiveSkill):
    name: Literal["Imperial Panoply"] = "Imperial Panoply"
    status_name: Literal["Armored Crab Carapace"] = "Armored Crab Carapace"
    version: Literal["4.6"] = "4.6"
    regenerate_when_revive: bool = False

    def event_handler_ACTION_END(
        self, event: ActionEndEventArguments, match: Match
    ) -> list[CreateObjectAction | RemoveObjectAction | ChangeObjectUsageAction]:
        """
        when any shield exist in our field except Armored Crab Carapace, remove all
        shield and gain new Armored Crab Carapace stacks.
        """
        if event.action.position.player_idx != self.position.player_idx:
            return []
        shield_status: list[StatusBase] = self.query(
            match,
            "our team_status icon_type=shield and our character status icon_type=shield",  # noqa
        )  # type: ignore
        armored_crab_status: list[StatusBase] = [
            x for x in shield_status if x.name == "Armored Crab Carapace"
        ]
        assert len(armored_crab_status) < 2
        other_shield_status: list[StatusBase] = [
            x for x in shield_status if x.name != "Armored Crab Carapace"
        ]
        if len(other_shield_status) == 0:
            return []
        # remove all shield, and create new Armored Crab Carapace stacks
        usage = len(other_shield_status) * 2
        if len(armored_crab_status) == 1:
            usage += armored_crab_status[0].usage
        ret: list[
            CreateObjectAction | RemoveObjectAction | ChangeObjectUsageAction
        ] = []
        for status in shield_status:
            ret.append(RemoveObjectAction(object_position=status.position))
        talent: MoltenMail_4_6 | None = self.query_one(match, "self talent")  # type: ignore  # noqa
        if talent is not None and talent.usage > 0:
            usage += 2
            ret.append(
                ChangeObjectUsageAction(
                    object_position=talent.position, change_usage=-1
                )
            )
        ret.append(
            CreateObjectAction(
                object_name="Armored Crab Carapace",
                object_position=self.position.set_area(
                    ObjectPositionType.CHARACTER_STATUS
                ),
                object_arguments={"usage": usage},
            )
        )
        return ret


# Talents


class MoltenMail_4_6(TalentBase):
    name: Literal["Molten Mail"]
    version: Literal["4.6"] = "4.6"
    character_name: Literal["Emperor of Fire and Iron"] = "Emperor of Fire and Iron"
    cost: Cost = Cost(elemental_dice_color=DieColor.PYRO, elemental_dice_number=1)
    usage: int = 1

    def is_valid(self, match: Match) -> bool:
        if self.position.area != ObjectPositionType.HAND:
            # not in hand, cannot equip
            raise AssertionError("Talent is not in hand")
        return len(self.get_targets(match)) > 0

    def get_targets(self, match: Match) -> list[ObjectPosition]:
        assert self.position.area != ObjectPositionType.CHARACTER
        ret: list[ObjectPosition] = []
        for c in match.player_tables[self.position.player_idx].characters:
            if c.name == self.character_name and c.is_alive:
                ret.append(c.position)
        return ret

    def get_actions(self, target: ObjectPosition | None, match: Match) -> List[Actions]:
        ret = super().get_actions(target, match)
        # apply Pyro Application to the Emperor of Fire and Iron with this card equipped
        assert target is not None
        ret.append(
            MakeDamageAction(
                damage_value_list=[
                    DamageValue.create_element_application(
                        self.position, target, DamageElementalType.PYRO, self.cost
                    )
                ]
            )
        )
        return ret

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Match
    ) -> list[Actions]:
        # reset usage
        self.usage = 1
        return []


# character base


# character class name should contain its version.
class EmperorOfFireAndIron_4_6(CharacterBase):
    name: Literal["Emperor of Fire and Iron"]
    version: Literal["4.6"] = "4.6"
    element: ElementType = ElementType.PYRO
    max_hp: int = 6
    max_charge: int = 2
    skills: list[
        PhysicalNormalAttackBase
        | BusterBlaze
        | BattleLineDetonation
        | SearingBlast
        | ImperialPanoply
    ] = []
    faction: list[FactionType] = [FactionType.MONSTER]
    weapon_type: WeaponType = WeaponType.OTHER

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name="Shatterclamp Strike",
                cost=PhysicalNormalAttackBase.get_cost(self.element),
            ),
            BusterBlaze(),
            BattleLineDetonation(),
            SearingBlast(),
            ImperialPanoply(),
        ]


desc: dict[str, DescDictType] = {
    "CHARACTER/Emperor of Fire and Iron": {
        "names": {"en-US": "Emperor of Fire and Iron", "zh-CN": "铁甲熔火帝皇"},
        "descs": {"4.6": {"en-US": "", "zh-CN": ""}},
        "image_path": "https://api.ambr.top/assets/UI/gcg/UI_Gcg_CardFace_Char_Monster_HermitCrabPrimo.png",  # noqa
        "id": 2304,
    },
    "SKILL_Emperor of Fire and Iron_NORMAL_ATTACK/Shatterclamp Strike": {
        "names": {"en-US": "Shatterclamp Strike", "zh-CN": "重钳碎击"},
        "descs": {
            "4.6": {"en-US": "Deals 2 Physical DMG.", "zh-CN": "造成2点物理伤害。"}
        },
    },
    "SKILL_Emperor of Fire and Iron_ELEMENTAL_SKILL/Buster Blaze": {
        "names": {"en-US": "Buster Blaze", "zh-CN": "烈焰燃绽"},
        "descs": {
            "4.6": {
                "en-US": "Deals 1 Pyro DMG. If this character has at least 7 Armored Crab Carapace stacks, this DMG +1.\nAfter that, this character gains 2 Armored Crab Carapace stacks.",  # noqa
                "zh-CN": "造成1点火元素伤害；如果本角色附属有至少7层重甲蟹壳，则此伤害+1。\n然后，本角色附属2层重甲蟹壳。",  # noqa
            }
        },
    },
    "CHARACTER_STATUS/Armored Crab Carapace": {
        "names": {"en-US": "Armored Crab Carapace", "zh-CN": "重甲蟹壳"},
        "descs": {
            "4.6": {
                "en-US": "Shield\nEach stack provides 1 Shield to protect the equipped character.",  # noqa
                "zh-CN": "护盾\n每层提供1点护盾，保护所附属角色。",
            }
        },
    },
    "SKILL_Emperor of Fire and Iron_ELEMENTAL_BURST/Battle-Line Detonation": {
        "names": {"en-US": "Battle-Line Detonation", "zh-CN": "战阵爆轰"},
        "descs": {
            "4.6": {
                "en-US": "This character's Prepare Skill|s1:prepares: Searing Blast.",
                "zh-CN": "本角色准备技能：炽烈轰破。",
            }
        },
    },
    "CHARACTER_STATUS/Searing Blast": {
        "names": {"en-US": "Searing Blast", "zh-CN": "炽烈轰破"},
        "descs": {
            "4.6": {
                "en-US": "Elemental Burst\n(Prepare for 1 turn)\nDeals 1 Pyro DMG, deals 2 Piercing DMG to all opposing standby characters. This skill deals +1 Pyro DMG for every 2 Armored Crab Carapace stacks this character has.",  # noqa
                "zh-CN": "元素爆发\n（需准备1个行动轮）\n造成1点火元素伤害，对敌方所有后台角色造成2点穿透伤害。本角色每附属有2层重甲蟹壳，就使此技能造成的火元素伤害+1。",  # noqa
            }
        },
    },
    "SKILL_Emperor of Fire and Iron_PASSIVE/Imperial Panoply": {
        "names": {"en-US": "Imperial Panoply", "zh-CN": "帝王甲胄"},
        "descs": {
            "4.6": {
                "en-US": "(Passive) When combat begins: Gain 5 initial Armored Crab Carapace stacks.\nAfter your side performs any action: If your side has any Shield Status or Shield Combat Status other than Armored Crab Carapace, these other effects will be canceled. For each effect canceled, this character gains 2 Armored Crab Carapace stacks.",  # noqa
                "zh-CN": "【被动】战斗开始时：初始附属5层重甲蟹壳。\n我方执行任意行动后：如果我方场上存在重甲蟹壳以外的护盾状态或护盾出战状态，则将其全部移除；每移除1个，就使角色附属2层重甲蟹壳。",  # noqa
            }
        },
    },
    "SKILL_Emperor of Fire and Iron_ELEMENTAL_BURST/Searing Blast": {
        "names": {"en-US": "Searing Blast", "zh-CN": "炽烈轰破"},
        "descs": {
            "4.6": {
                "en-US": "(Prepare for 1 turn)\nDeals 1 Pyro DMG, deals 2 Piercing DMG to all opposing standby characters. This skill deals +1 Pyro DMG for every 2 Armored Crab Carapace stacks this character has.",  # noqa
                "zh-CN": "（需准备1个行动轮）\n造成1点火元素伤害，对敌方所有后台角色造成2点穿透伤害。本角色每附属有2层重甲蟹壳，就使此技能造成的火元素伤害+1。",  # noqa
            }
        },
    },
    "TALENT_Emperor of Fire and Iron/Molten Mail": {
        "names": {"en-US": "Molten Mail", "zh-CN": "熔火铁甲"},
        "descs": {
            "4.6": {
                "en-US": "When played: Apply Pyro Application to the Emperor of Fire and Iron with this card equipped.\nAfter your Shield Status other than Armored Crab Carapace or Shield Combat Status is removed: The Emperor of Fire and Iron with this card equipped gains 2 stacks of Armored Crab Carapace. (Once per Round)\n(You must have Emperor of Fire and Iron in your deck to add this card to your deck.)",  # noqa
                "zh-CN": "入场时：对装备有此牌的铁甲熔火帝皇附着火元素。\n我方除重甲蟹壳以外的护盾状态或护盾出战状态被移除后：装备有此牌的铁甲熔火帝皇附属2层重甲蟹壳。（每回合1次）\n（牌组中包含铁甲熔火帝皇，才能加入牌组）",  # noqa
            }
        },
        "image_path": "https://api.ambr.top/assets/UI/gcg/UI_Gcg_CardFace_Modify_Talent_HermitCrabPrimo.png",  # noqa
        "id": 223041,
    },
}


register_class(
    EmperorOfFireAndIron_4_6
    | ArmoredCrabCarapace_4_6
    | SearingBlast_4_6
    | MoltenMail_4_6,
    desc,
)
