from typing import List, Literal

from lpsim.server.action import (
    Actions,
    CreateDiceAction,
    RemoveObjectAction,
    SwitchCharacterAction,
)
from lpsim.server.character.character_base import (
    CharacterBase,
    ElementalBurstBase,
    ElementalSkillBase,
    PhysicalNormalAttackBase,
    SkillTalent,
)
from lpsim.server.consts import (
    CostLabels,
    DamageElementalType,
    DamageType,
    DieColor,
    ElementType,
    FactionType,
    IconType,
    WeaponType,
)
from lpsim.server.event import RoundEndEventArguments, RoundPrepareEventArguments
from lpsim.server.match import Match, MatchConfig
from lpsim.server.modifiable_values import CostValue, DamageIncreaseValue
from lpsim.server.status.character_status.base import CharacterStatusBase
from lpsim.server.struct import Cost
from lpsim.server.summon.base import AttackerSummonBase
from lpsim.utils.class_registry import register_class
from lpsim.utils.desc_registry import DescDictType


class ManifestGale_4_6(CharacterStatusBase):
    name: Literal["Manifest Gale"] = "Manifest Gale"
    version: Literal["4.6"] = "4.6"
    usage: int = 1
    max_usage: int = 1
    icon_type: IconType = IconType.ELEMENT_ENCHANT_WIND

    def value_modifier_COST(
        self, value: CostValue, match: Match, mode: Literal["TEST", "REAL"]
    ) -> CostValue:
        if (
            value.cost.label & CostLabels.CHARGED_ATTACK.value > 0
            and value.cost.label & CostLabels.NORMAL_ATTACK.value > 0
            and self.position.satisfy(
                "both pidx=same cidx=same and target area=skill", target=value.position
            )
        ):
            # self use normal attack and is charged attack
            value.cost.decrease_cost(None)
        return value


class PressurizedCollapse_4_6(CharacterStatusBase):
    name: Literal["Pressurized Collapse"] = "Pressurized Collapse"
    version: Literal["4.6"] = "4.6"
    usage: int = 1
    max_usage: int = 1
    icon_type: IconType = IconType.OTHERS

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Match
    ) -> List[SwitchCharacterAction | RemoveObjectAction]:
        """
        At the end of every round, switch to this character.
        """
        if self.usage <= 0:  # pragma: no cover
            return []
        current_active = match.player_tables[
            self.position.player_idx
        ].active_character_idx
        if current_active == self.position.character_idx:
            # already active, only remove self
            return [RemoveObjectAction(object_position=self.position)]
        return [
            SwitchCharacterAction(
                player_idx=self.position.player_idx,
                character_idx=self.position.character_idx,
            ),
            RemoveObjectAction(object_position=self.position),
        ]


class DazzlingPolyhedron_4_6(AttackerSummonBase):
    name: Literal["Dazzling Polyhedron"]
    desc: Literal["", "talent"] = ""
    version: Literal["4.6"] = "4.6"
    usage: int = 3
    max_usage: int = 3
    damage: int = 1
    damage_elemental_type: DamageElementalType = DamageElementalType.ANEMO

    # def renew(self, obj: "DazzlingPolyhedron_4_6") -> None:
    #     super().renew(obj)
    #     if obj.desc == "talent" and self.desc != "talent":
    #         self.desc = "talent"

    def value_modifier_DAMAGE_INCREASE(
        self,
        value: DamageIncreaseValue,
        match: Match,
        mode: Literal["TEST", "REAL"],
    ) -> DamageIncreaseValue:
        if value.damage_type != DamageType.DAMAGE:
            # not damage, do nothing
            return value
        if value.target_position.player_idx == self.position.player_idx:
            # attack self, no nothing
            return value
        if value.damage_elemental_type != DamageElementalType.ANEMO:
            # not cryo or physical, do nothing
            return value
        # increase damage
        assert mode == "REAL"
        value.damage += 1
        return value

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Match
    ) -> List[CreateDiceAction]:
        if self.desc == "talent":
            return [
                CreateDiceAction(
                    player_idx=self.position.player_idx, number=1, color=DieColor.ANEMO
                )
            ]
        return []


class ParthianShot(PhysicalNormalAttackBase):
    name: Literal["Parthian Shot"] = "Parthian Shot"
    version: Literal["4.6"] = "4.6"
    damage: int = 2
    cost: Cost = PhysicalNormalAttackBase.get_cost(ElementType.ANEMO)

    def get_actions(self, match: Match) -> List[Actions]:
        target = self.query_one(match, "self status name='Manifest Gale'")
        table = match.player_tables[self.position.player_idx]
        if target is None or not table.charge_satisfied:
            return super().get_actions(match)
        ret: list[Actions] = [
            self.attack_opposite_active(match, self.damage, DamageElementalType.ANEMO),
            self.create_opposite_character_status(match, "Pressurized Collapse"),
            RemoveObjectAction(object_position=target.position),
            self.charge_self(1),
        ]  # type: ignore
        return ret


class WindRealmOfNasamjnin(ElementalSkillBase):
    name: Literal["Wind Realm of Nasamjnin"] = "Wind Realm of Nasamjnin"
    version: Literal["4.6"] = "4.6"
    damage_type: ElementType = ElementType.ANEMO
    damage: int = 3
    cost: Cost = Cost(elemental_dice_color=DieColor.ANEMO, elemental_dice_number=3)

    def get_actions(self, match: Match) -> list[Actions]:
        return super().get_actions(match) + [
            self.create_character_status("Manifest Gale")
        ]


class TheWindsSecretWays(ElementalBurstBase):
    name: Literal["The Wind's Secret Ways"] = "The Wind's Secret Ways"
    version: Literal["4.6"] = "4.6"
    damage_type: ElementType = ElementType.ANEMO
    damage: int = 1
    cost: Cost = Cost(
        elemental_dice_color=DieColor.ANEMO, elemental_dice_number=3, charge=2
    )

    def get_actions(self, match: MatchConfig) -> list[Actions]:
        ret = super().get_actions(match)
        has_talent = self.is_talent_equipped(match)
        args = {}
        if has_talent:
            # have talent, immediately create one die
            ret += [
                CreateDiceAction(
                    player_idx=self.position.player_idx, number=1, color=DieColor.ANEMO
                )
            ]
            args["desc"] = "talent"
        ret += [self.create_summon("Dazzling Polyhedron", args)]
        return ret


class Faruzan_4_6(CharacterBase):
    name: Literal["Faruzan"]
    version: Literal["4.6"] = "4.6"
    element: ElementType = ElementType.ANEMO
    max_hp: int = 10
    max_charge: int = 2
    skills: list[ParthianShot | WindRealmOfNasamjnin | TheWindsSecretWays] = []
    faction: list[FactionType] = [FactionType.SUMERU]
    weapon_type: WeaponType = WeaponType.BOW

    def _init_skills(self) -> None:
        self.skills = [
            ParthianShot(),
            WindRealmOfNasamjnin(),
            TheWindsSecretWays(),
        ]


class TheWondrousPathOfTruth_4_6(SkillTalent):
    name: Literal["The Wondrous Path of Truth"]
    version: Literal["4.6"] = "4.6"
    character_name: Literal["Faruzan"] = "Faruzan"
    cost: Cost = Cost(
        elemental_dice_color=DieColor.ANEMO, elemental_dice_number=3, charge=2
    )
    skill: Literal["The Wind's Secret Ways"] = "The Wind's Secret Ways"


desc: dict[str, DescDictType] = {
    "CHARACTER/Faruzan": {
        "names": {"en-US": "Faruzan", "zh-CN": "珐露珊"},
        "descs": {"4.6": {"en-US": "", "zh-CN": ""}},
        "image_path": "https://api.ambr.top/assets/UI/gcg/UI_Gcg_CardFace_Char_Avatar_Faruzan.png",  # noqa
        "id": 1509,
    },
    "SKILL_Faruzan_NORMAL_ATTACK/Parthian Shot": {
        "names": {"en-US": "Parthian Shot", "zh-CN": "迴身箭术"},
        "descs": {
            "4.6": {"en-US": "Deals 2 Physical DMG.", "zh-CN": "造成2点物理伤害。"}
        },
    },
    "SKILL_Faruzan_ELEMENTAL_SKILL/Wind Realm of Nasamjnin": {
        "names": {"en-US": "Wind Realm of Nasamjnin", "zh-CN": "非想风天"},
        "descs": {
            "4.6": {
                "en-US": "Deals 3 Anemo DMG. This character gains Manifest Gale.",
                "zh-CN": "造成3点风元素伤害，本角色附属疾风示现。",
            }
        },
    },
    "CHARACTER_STATUS/Manifest Gale": {
        "names": {"en-US": "Manifest Gale", "zh-CN": "疾风示现"},
        "descs": {
            "4.6": {
                "en-US": "When the character to which this is attached uses Charged Attack: Spend 1 less Unaligned Element, Physical DMG dealt converted to Anemo DMG, and attaches Pressurized Collapse to the target character.\nUsage(s): 1",  # noqa
                "zh-CN": "所附属角色进行重击时：少花费1个无色元素，造成的物理伤害变为风元素伤害，并且使目标角色附属风压坍陷。\n可用次数：1",  # noqa
            }
        },
    },
    "CHARACTER_STATUS/Pressurized Collapse": {
        "names": {"en-US": "Pressurized Collapse", "zh-CN": "风压坍陷"},
        "descs": {
            "4.6": {
                "en-US": "At the End Phase, you will switch to this character.",
                "zh-CN": "结束阶段，我方切换到此角色。",
            }
        },
    },
    "SKILL_Faruzan_ELEMENTAL_BURST/The Wind's Secret Ways": {
        "names": {"en-US": "The Wind's Secret Ways", "zh-CN": "抟风秘道"},
        "descs": {
            "4.6": {
                "en-US": "Deals 1 Anemo DMG, summons 1 Dazzling Polyhedron.",
                "zh-CN": "造成1点风元素伤害，召唤赫耀多方面体。",
            }
        },
    },
    "SUMMON/Dazzling Polyhedron": {
        "names": {"en-US": "Dazzling Polyhedron", "zh-CN": "赫耀多方面体"},
        "descs": {
            "4.6": {
                "en-US": "End Phase: Deal 1 Anemo DMG.\nUsage(s): 3\nWhen this Summon is on the field: Opposing character(s) take +1 Anemo DMG.",  # noqa
                "zh-CN": "结束阶段：造成1点风元素伤害。\n可用次数：3\n此召唤物在场时：敌方角色受到的风元素伤害+1。",  # noqa
            }
        },
    },
    "SUMMON/Dazzling Polyhedron_talent": {
        "names": {"en-US": "Dazzling Polyhedron", "zh-CN": "赫耀多方面体"},
        "descs": {
            "4.6": {
                "en-US": "End Phase: Deal 1 Anemo DMG.\nUsage(s): 3\nWhen this Summon is on the field: Opposing character(s) take +1 Anemo DMG. When this card enters play and when the Action Phase begins: Create 1 Anemo Die.",  # noqa
                "zh-CN": "结束阶段：造成1点风元素伤害。\n可用次数：3\n此召唤物在场时：敌方角色受到的风元素伤害+1。\n入场时和行动阶段开始时生成1个风元素骰。",  # noqa
            }
        },
    },
    "TALENT_Faruzan/The Wondrous Path of Truth": {
        "names": {"en-US": "The Wondrous Path of Truth", "zh-CN": "妙道合真"},
        "descs": {
            "4.6": {
                "en-US": "Combat Action: When your active character is Faruzan, equip this card.\nAfter Faruzan equips this card, immediately use The Wind's Secret Ways.\nWhen the Dazzling Polyhedron created by Faruzan who has this card equipped enters play and when the Action Phase begins: Create 1 Anemo Die.\n(You must have Faruzan in your deck to add this card to your deck.)",  # noqa
                "zh-CN": "战斗行动：我方出战角色为珐露珊时，装备此牌。\n珐露珊装备此牌后，立刻使用一次抟风秘道。\n装备有此牌的珐露珊所生成的赫耀多方面体，会在其入场时和行动阶段开始时生成1个风元素骰。\n（牌组中包含珐露珊，才能加入牌组）",  # noqa
            }
        },
        "image_path": "https://api.ambr.top/assets/UI/gcg/UI_Gcg_CardFace_Modify_Talent_Faruzan.png",  # noqa
        "id": 215091,
    },
}


register_class(
    Faruzan_4_6
    | TheWondrousPathOfTruth_4_6
    | ManifestGale_4_6
    | PressurizedCollapse_4_6
    | DazzlingPolyhedron_4_6,
    desc,
)
