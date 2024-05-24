from typing import Literal
from lpsim.server.action import (
    ActionTypes,
    Actions,
    MakeDamageAction,
    RemoveObjectAction,
)
from lpsim.server.character.character_base import (
    CharacterBase,
    ElementalBurstBase,
    ElementalSkillBase,
    PhysicalNormalAttackBase,
    SkillTalent,
)
from lpsim.server.consts import (
    DamageElementalType,
    DamageType,
    DieColor,
    ElementType,
    FactionType,
    IconType,
    ObjectPositionType,
    WeaponType,
)
from lpsim.server.event import (
    ChooseCharacterEventArguments,
    MakeDamageEventArguments,
    RoundPrepareEventArguments,
    SwitchCharacterEventArguments,
)
from lpsim.server.match import Match
from lpsim.server.modifiable_values import DamageIncreaseValue, DamageValue
from lpsim.server.status.team_status.base import UsageWithRoundRestrictionTeamStatus
from lpsim.server.struct import Cost
from lpsim.utils.class_registry import register_class
from lpsim.utils.desc_registry import DescDictType


class GrassRingOfSanctification_4_6(UsageWithRoundRestrictionTeamStatus):
    name: Literal["Grass Ring of Sanctification"] = "Grass Ring of Sanctification"
    version: Literal["4.6"] = "4.6"
    max_usage: int = 3
    usage: int = 3
    max_usage_one_round: int = 1
    icon_type: IconType = IconType.OTHERS

    def _switched_action(
        self, player_idx: int, match: Match
    ) -> list[MakeDamageAction | RemoveObjectAction]:
        """
        when switched and is self switch and has usage, heal and make damage
        """
        if not self.has_usage():
            return []
        if player_idx != self.position.player_idx:
            return []
        # do heal and damage
        self.use()
        damage_target: CharacterBase = self.query_one(match, "opponent active")  # type: ignore  # noqa
        our_target: list[CharacterBase] = self.query(
            match, "our character is_alive=true"
        )  # type: ignore
        target: CharacterBase = self.query_one(match, "our active")  # type: ignore
        for t in our_target:
            if t.damage_taken > target.damage_taken:
                target = t
        ret: list[MakeDamageAction | RemoveObjectAction] = [
            MakeDamageAction(
                damage_value_list=[
                    DamageValue(
                        position=self.position,
                        target_position=damage_target.position,
                        damage_type=DamageType.DAMAGE,
                        damage=1,
                        damage_elemental_type=DamageElementalType.ELECTRO,
                        cost=Cost(),
                    ),
                    DamageValue.create_heal(self.position, target.position, -1, Cost()),
                ]
            )
        ]
        if self.usage <= 0:
            ret.append(RemoveObjectAction(object_position=self.position))
        return ret

    def event_handler_SWITCH_CHARACTER(
        self, event: SwitchCharacterEventArguments, match: Match
    ):
        return self._switched_action(event.action.player_idx, match)

    def event_handler_CHOOSE_CHARACTER(
        self, event: ChooseCharacterEventArguments, match: Match
    ):
        return self._switched_action(event.action.player_idx, match)


# Skills


class SanctifyingRing(ElementalSkillBase):
    name: Literal["Sanctifying Ring"] = "Sanctifying Ring"
    damage: int = 0
    damage_type: DamageElementalType = DamageElementalType.PIERCING
    cost: Cost = Cost(elemental_dice_color=DieColor.ELECTRO, elemental_dice_number=3)

    def get_actions(self, match: Match) -> list[Actions]:
        """
        Attack and create object
        """
        ret: list[Actions] = [
            self.create_team_status("Grass Ring of Sanctification"),
            self.charge_self(1),
        ]
        me: CharacterBase = self.query_one(match, "self")  # type: ignore
        if me.hp >= 6:
            ret = [
                MakeDamageAction(
                    damage_value_list=[
                        DamageValue(
                            position=self.position,
                            damage_type=DamageType.DAMAGE,
                            target_position=me.position,
                            damage=2,
                            damage_elemental_type=DamageElementalType.PIERCING,
                            cost=self.cost,
                        )
                    ]
                )
            ] + ret
        return ret


class GyoeiNarukamiKariyamaRite(ElementalBurstBase):
    name: Literal["Gyoei Narukami Kariyama Rite"] = "Gyoei Narukami Kariyama Rite"
    damage: int = 4
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color=DieColor.ELECTRO, elemental_dice_number=3, charge=2
    )

    def get_actions(self, match: Match) -> list[Actions]:
        ret = super().get_actions(match)
        damage_action = ret[1]
        assert damage_action.type == ActionTypes.MAKE_DAMAGE
        # heal self
        me: CharacterBase = self.query_one(match, "self")  # type: ignore
        damage_action.damage_value_list.append(
            DamageValue.create_heal(self.position, me.position, -2, self.cost)
        )
        return ret


# Talents


class ToWardWeakness_4_6(SkillTalent):
    name: Literal["To Ward Weakness"]
    version: Literal["4.6"] = "4.6"
    character_name: Literal["Kuki Shinobu"] = "Kuki Shinobu"
    cost: Cost = Cost(
        elemental_dice_color=DieColor.ELECTRO, elemental_dice_number=3, charge=2
    )
    skill: Literal["Gyoei Narukami Kariyama Rite"] = "Gyoei Narukami Kariyama Rite"
    usage: int = 1

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Match
    ) -> list[Actions]:
        # reset usage
        self.usage = 1
        return []

    def event_handler_MAKE_DAMAGE(
        self,
        event: MakeDamageEventArguments,
        match: Match,
    ) -> list[MakeDamageAction]:
        """
        when make damage, check whether this character's hp is 0. if so,
        heal it by self.heal hp.

        Using make damage action, so it will trigger immediately before
        receiving any other damage, and can be defeated by other damage.
        """
        if self.position.area != ObjectPositionType.CHARACTER:
            # not equipped
            return []
        character: CharacterBase = self.query_one(match, "self")  # type: ignore
        if character.hp > 0:
            # hp not 0, do nothing
            return []
        if self.usage <= 0:
            # no usage, do nothing
            return []
        # heal this character by 1
        self.usage -= 1
        return [
            MakeDamageAction(
                damage_value_list=[
                    DamageValue.create_heal(
                        self.position,
                        character.position,
                        -1,
                        Cost(),  # Although self have cost, this heal have no cost?
                    ),
                ],
            )
        ]

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Match, mode: Literal["TEST", "REAL"]
    ) -> DamageIncreaseValue:
        """
        If this character's hp is less than 6, increase damage by 1.
        """
        if self.position.area != ObjectPositionType.CHARACTER:
            # not equipped
            return value
        character: CharacterBase = self.query_one(match, "self")  # type: ignore
        if character.hp >= 6:
            # hp not less than 6, do nothing
            return value
        if value.is_corresponding_character_use_damage_skill(
            character.position, match, None
        ):
            value.damage += 1
        return value


# character base


# character class name should contain its version.
class KukiShinobu_4_6(CharacterBase):
    name: Literal["Kuki Shinobu"]
    version: Literal["4.6"] = "4.6"
    element: ElementType = ElementType.ELECTRO
    max_hp: int = 10
    max_charge: int = 2
    skills: list[
        PhysicalNormalAttackBase | SanctifyingRing | GyoeiNarukamiKariyamaRite
    ] = []
    faction: list[FactionType] = [FactionType.INAZUMA]
    weapon_type: WeaponType = WeaponType.SWORD

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name="Shinobu's Shadowsword",
                cost=PhysicalNormalAttackBase.get_cost(self.element),
            ),
            SanctifyingRing(),
            GyoeiNarukamiKariyamaRite(),
        ]


desc: dict[str, DescDictType] = {
    "CHARACTER/Kuki Shinobu": {
        "names": {"en-US": "Kuki Shinobu", "zh-CN": "久岐忍"},
        "descs": {"4.6": {"en-US": "", "zh-CN": ""}},
        "image_path": "https://api.ambr.top/assets/UI/gcg/UI_Gcg_CardFace_Char_Avatar_Shinobu.png",  # noqa
        "id": 1411,
    },
    "SKILL_Kuki Shinobu_NORMAL_ATTACK/Shinobu's Shadowsword": {
        "names": {"en-US": "Shinobu's Shadowsword", "zh-CN": "忍流飞刃斩"},
        "descs": {
            "4.6": {"en-US": "Deals 2 Physical DMG.", "zh-CN": "造成2点物理伤害。"}
        },
    },
    "SKILL_Kuki Shinobu_ELEMENTAL_SKILL/Sanctifying Ring": {
        "names": {"en-US": "Sanctifying Ring", "zh-CN": "越祓雷草之轮"},
        "descs": {
            "4.6": {
                "en-US": "Summons a Grass Ring of Sanctification. If this character has at least 6 HP, then she deals 2 Piercing DMG to herself.",  # noqa
                "zh-CN": "生成越祓草轮。如果本角色生命值至少为6，则对自身造成2点穿透伤害。",  # noqa
            }
        },
    },
    "TEAM_STATUS/Grass Ring of Sanctification": {
        "names": {"en-US": "Grass Ring of Sanctification", "zh-CN": "越祓草轮"},
        "descs": {
            "4.6": {
                "en-US": "After you switch characters: Deal 1 Electro DMG, heal the character on your team that has taken the most damage for 1 HP. (Once per Round)\nUsage(s): 3",  # noqa
                "zh-CN": "我方切换角色后：造成1点雷元素伤害，治疗我方受伤最多的角色1点。（每回合1次）\n可用次数：3",  # noqa
            }
        },
    },
    "SKILL_Kuki Shinobu_ELEMENTAL_BURST/Gyoei Narukami Kariyama Rite": {
        "names": {"en-US": "Gyoei Narukami Kariyama Rite", "zh-CN": "御咏鸣神刈山祭"},
        "descs": {
            "4.6": {
                "en-US": "Deals 4 Electro DMG, heals this character for 2 HP.",
                "zh-CN": "造成4点雷元素伤害，治疗本角色2点。",
            }
        },
    },
    "TALENT_Kuki Shinobu/To Ward Weakness": {
        "names": {"en-US": "To Ward Weakness", "zh-CN": "割舍软弱之心"},
        "descs": {
            "4.6": {
                "en-US": "Combat Action: When your active character is Kuki Shinobu, equip this card.\nAfter Kuki Shinobu equips this card, immediately use Gyoei Narukami Kariyama Rite once.\nWhen Kuki Shinobu, who has this card equipped, is defeated, she will not be defeated but will instead heal herself to 1 HP. (Once per Round)\nIf Kuki Shinobu, who has this card equipped, does not have more than 5 HP, deal +1 DMG.\n(You must have Kuki Shinobu in your deck to add this card to your deck.)",  # noqa
                "zh-CN": "战斗行动：我方出战角色为久岐忍时，装备此牌。\n久岐忍装备此牌后，立刻使用一次御咏鸣神刈山祭。\n装备有此牌的久岐忍被击倒时：角色免于被击倒，并治疗该角色到1点生命值。（每回合1次）\n如果装备有此牌的久岐忍生命值不多于5，则该角色造成的伤害+1。\n（牌组中包含久岐忍，才能加入牌组）",  # noqa
            }
        },
        "image_path": "https://api.ambr.top/assets/UI/gcg/UI_Gcg_CardFace_Modify_Talent_Shinobu.png",  # noqa
        "id": 214111,
    },
}


register_class(
    KukiShinobu_4_6 | ToWardWeakness_4_6 | GrassRingOfSanctification_4_6, desc
)
