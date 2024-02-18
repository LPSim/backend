from typing import Dict, List, Literal

from ....match import Match
from ....character import CharacterBase
from ....action import (
    ActionTypes,
    Actions,
    ChangeObjectUsageAction,
    DrawCardAction,
    MakeDamageAction,
)
from ....character.character_base import (
    ElementalBurstBase,
    ElementalSkillBase,
    PhysicalNormalAttackBase,
    SkillTalent,
)
from ....consts import (
    ELEMENT_TO_DAMAGE_TYPE,
    DamageElementalType,
    DamageType,
    DieColor,
    ElementType,
    ElementalReactionType,
    FactionType,
    IconType,
    ObjectPositionType,
    WeaponType,
)
from ....event import (
    ReceiveDamageEventArguments,
    RoundEndEventArguments,
    RoundPrepareEventArguments,
)
from ....modifiable_values import DamageValue
from ....status.character_status.base import PrepareCharacterStatus
from ....struct import Cost
from ....summon.base import AttackerSummonBase
from .....utils import register_class, DescDictType


class MujiMujiDaruma_4_4(AttackerSummonBase):
    name: Literal["Muji-Muji Daruma"] = "Muji-Muji Daruma"
    version: Literal["4.4"] = "4.4"
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.ANEMO
    damage: int = 1
    heal: int = 2

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Match
    ) -> List[MakeDamageAction | ChangeObjectUsageAction]:
        ret = super().event_handler_ROUND_END(event, match)
        table = match.player_tables[self.position.player_idx]
        characters = table.characters
        # select character with most damage taken
        selected_character = characters[table.active_character_idx]
        for c in characters:
            if c.is_alive and c.damage_taken > selected_character.damage_taken:
                selected_character = c
        # heal character, and do default actions
        assert ret[0].type == ActionTypes.MAKE_DAMAGE
        ret[0].damage_value_list.append(
            DamageValue(
                position=self.position,
                damage_type=DamageType.HEAL,
                target_position=selected_character.position,
                damage=-self.heal,
                damage_elemental_type=DamageElementalType.HEAL,
                cost=Cost(),
            )
        )
        return ret


class FuufuuWhirlwindKickStatus_4_4(PrepareCharacterStatus):
    name: Literal["Fuufuu Whirlwind Kick"] = "Fuufuu Whirlwind Kick"
    version: Literal["4.4"] = "4.4"
    character_name: Literal["Sayu"] = "Sayu"
    skill_name: Literal["Fuufuu Whirlwind Kick"] = "Fuufuu Whirlwind Kick"
    element: DamageElementalType = DamageElementalType.ANEMO
    icon_type: IconType = IconType.SPECIAL

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Match
    ) -> List[Actions]:
        # if self make swirl, record swirled element
        if self.element != DamageElementalType.ANEMO:
            # not anemo, do nothing
            return []
        if not self.position.check_position_valid(
            event.final_damage.position,
            match,
            player_idx_same=True,
            character_idx_same=True,
            target_area=ObjectPositionType.SKILL,
        ):
            # not self use skill, skip
            return []
        if (
            event.final_damage.damage_from_element_reaction
            or event.final_damage.element_reaction != ElementalReactionType.SWIRL
        ):
            # not swirl or from elemental reaction, skip
            return []
        # record swirled element
        elements = event.final_damage.reacted_elements
        assert elements[0] == ElementType.ANEMO
        self.element = ELEMENT_TO_DAMAGE_TYPE[elements[1]]
        return []


class YooHooArtFuuinDash(ElementalSkillBase):
    name: Literal["Yoohoo Art: Fuuin Dash"] = "Yoohoo Art: Fuuin Dash"
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = Cost(elemental_dice_color=DieColor.ANEMO, elemental_dice_number=3)

    def get_actions(self, match: Match) -> List[Actions]:
        return super().get_actions(match) + [
            self.create_character_status("Fuufuu Whirlwind Kick"),
        ]


class FuufuuWhirlwindKick(ElementalSkillBase):
    name: Literal["Fuufuu Whirlwind Kick"] = "Fuufuu Whirlwind Kick"
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = Cost()

    def is_valid(self, match: Match) -> bool:
        return False

    def get_actions(self, match: Match) -> List[Actions]:
        # first change self element based on status, then call super
        status = (
            match.player_tables[self.position.player_idx]
            .characters[self.position.character_idx]
            .status
        )
        for s in status:
            if s.name == "Fuufuu Whirlwind Kick":
                self.damage_type = s.element  # type: ignore
                break
        else:
            raise AssertionError("No Fuufuu Whirlwind Kick status")
        return [self.attack_opposite_active(match, self.damage, self.damage_type)]


class YoohooArtMujinaFlurry(ElementalBurstBase):
    name: Literal["Yoohoo Art: Mujina Flurry"] = "Yoohoo Art: Mujina Flurry"
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = Cost(
        elemental_dice_color=DieColor.ANEMO, elemental_dice_number=3, charge=2
    )

    def get_actions(self, match: Match) -> List[Actions]:
        return super().get_actions(match) + [
            self.create_summon("Muji-Muji Daruma"),
        ]


class SkivingNewAndImproved_4_4(SkillTalent):
    name: Literal["Skiving: New and Improved"]
    version: Literal["4.4"] = "4.4"
    cost: Cost = Cost(elemental_dice_color=DieColor.ANEMO, elemental_dice_number=3)
    skill: Literal["Yoohoo Art: Fuuin Dash"] = "Yoohoo Art: Fuuin Dash"
    character_name: Literal["Sayu"] = "Sayu"
    usage: int = 1
    max_usage_per_round: int = 1

    def equip(self, match: Match) -> List[Actions]:
        self.usage = self.max_usage_per_round
        return []

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Match
    ) -> List[Actions]:
        self.usage = self.max_usage_per_round
        return []

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Match
    ) -> List[DrawCardAction]:
        if self.usage <= 0:
            # already used
            return []
        if not self.position.check_position_valid(
            event.final_damage.position,
            match,
            player_idx_same=True,
            character_idx_same=True,
            target_area=ObjectPositionType.SKILL,
            source_area=ObjectPositionType.CHARACTER,
            source_is_active_character=True,
        ):
            # not self skill or not equipped or self not active
            return []
        if event.final_damage.element_reaction != ElementalReactionType.SWIRL:
            # not swirl
            return []
        # draw card
        self.usage -= 1
        return [
            DrawCardAction(
                player_idx=self.position.player_idx,
                number=2,
                draw_if_filtered_not_enough=True,
            )
        ]


class Sayu_4_4(CharacterBase):
    name: Literal["Sayu"]
    version: Literal["4.4"] = "4.4"
    element: ElementType = ElementType.ANEMO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase
        | YooHooArtFuuinDash
        | FuufuuWhirlwindKick
        | YoohooArtMujinaFlurry
    ] = []
    faction: List[FactionType] = [FactionType.INAZUMA]
    weapon_type: WeaponType = WeaponType.CLAYMORE

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name="Shuumatsuban Ninja Blade",
                cost=PhysicalNormalAttackBase.get_cost(self.element),
            ),
            YooHooArtFuuinDash(),
            FuufuuWhirlwindKick(),
            YoohooArtMujinaFlurry(),
        ]


desc: Dict[str, DescDictType] = {
    "CHARACTER/Sayu": {
        "names": {"en-US": "Sayu", "zh-CN": "早柚"},
        "descs": {"4.4": {"en-US": "", "zh-CN": ""}},
        "image_path": "cardface/Char_Avatar_Sayu.png",  # noqa
        "id": 1507,
    },
    "SKILL_Sayu_NORMAL_ATTACK/Shuumatsuban Ninja Blade": {
        "names": {"en-US": "Shuumatsuban Ninja Blade", "zh-CN": "忍刀·终末番"},
        "descs": {
            "4.4": {"en-US": "Deals 2 Physical DMG.", "zh-CN": "造成2点物理伤害。"}
        },
    },
    "SKILL_Sayu_ELEMENTAL_SKILL/Yoohoo Art: Fuuin Dash": {
        "names": {"en-US": "Yoohoo Art: Fuuin Dash", "zh-CN": "呜呼流·风隐急进"},
        "descs": {
            "4.4": {
                "en-US": "Deals 1 Anemo DMG, and this character Prepare Skill|s1:prepares: Fuufuu Whirlwind Kick.\nIf this usage of the skill triggers Swirl, then Fuufuu Whirlwind Kick is converted to DMG of the Swirled Element.",  # noqa
                "zh-CN": "造成1点风元素伤害，本角色准备技能：风风轮舞踢。\n如果当前技能引发了扩散，则风风轮舞踢将改为造成被扩散元素的伤害。",  # noqa
            }
        },
    },
    "CHARACTER_STATUS/Fuufuu Whirlwind Kick": {
        "names": {"en-US": "Fuufuu Whirlwind Kick", "zh-CN": "风风轮舞踢"},
        "descs": {
            "4.4": {
                "en-US": "Elemental Skill\n(Prepare for 1 turn)\nDeals 2 Anemo DMG (or the Swirled Element's DMG)",  # noqa
                "zh-CN": "元素战技\n（需准备1个行动轮）\n造成2点风元素伤害（或被扩散元素的伤害）。",  # noqa
            }
        },
    },
    "SKILL_Sayu_ELEMENTAL_BURST/Yoohoo Art: Mujina Flurry": {
        "names": {"en-US": "Yoohoo Art: Mujina Flurry", "zh-CN": "呜呼流·影貉缭乱"},
        "descs": {
            "4.4": {
                "en-US": "Deals 1 Anemo DMG, summons 1 Muji-Muji Daruma.",
                "zh-CN": "造成1点风元素伤害，召唤不倒貉貉。",
            }
        },
    },
    "SUMMON/Muji-Muji Daruma": {
        "names": {"en-US": "Muji-Muji Daruma", "zh-CN": "不倒貉貉"},
        "descs": {
            "4.4": {
                "en-US": "End Phase: Deal 1 Anemo DMG, heal the character on your team that has taken the most damage for 2 HP.\nUsage(s): 2",  # noqa
                "zh-CN": "结束阶段：造成1点风元素伤害，治疗我方受伤最多的角色2点。\n可用次数：2",  # noqa
            }
        },
        "image_path": "cardface/Summon_Sayu.png",
    },
    "SKILL_Sayu_ELEMENTAL_SKILL/Fuufuu Whirlwind Kick": {
        "names": {"en-US": "Fuufuu Whirlwind Kick", "zh-CN": "风风轮舞踢"},
        "descs": {
            "4.4": {
                "en-US": "(Prepare for 1 turn)\nDeals 2 Anemo DMG (or the Swirled Element's DMG)",  # noqa
                "zh-CN": "（需准备1个行动轮）\n造成2点风元素伤害（或被扩散元素的伤害）。",  # noqa
            }
        },
    },
    "TALENT_Sayu/Skiving: New and Improved": {
        "names": {"en-US": "Skiving: New and Improved", "zh-CN": "偷懒的新方法"},
        "descs": {
            "4.4": {
                "en-US": "Combat Action: When your active character is Sayu, equip this card.\nWhen Sayu equips this card, immediately use Yoohoo Art: Fuuin Dash once.\nWhen your Sayu who has this card equipped is the active character, draw 2 cards when you trigger a Swirl reaction. (Once per Round)\n(You must have Sayu in your deck to add this card to your deck.)",  # noqa
                "zh-CN": "战斗行动：我方出战角色为早柚时，装备此牌。\n早柚装备此牌后，立刻使用一次呜呼流·风隐急进。\n装备有此牌的早柚为出战角色期间，我方引发扩散反应时：抓2张牌。（每回合1次）\n（牌组中包含早柚，才能加入牌组）",  # noqa
            }
        },
        "image_path": "cardface/Modify_Constellation_Sayu.png",  # noqa
        "id": 215071,
    },
}


register_class(
    Sayu_4_4
    | MujiMujiDaruma_4_4
    | FuufuuWhirlwindKickStatus_4_4
    | SkivingNewAndImproved_4_4,
    desc,
)
