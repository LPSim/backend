from typing import Any, Dict, List, Literal

from ....action import (
    ActionTypes,
    Actions,
    ChangeObjectUsageAction,
    CreateObjectAction,
    DrawCardAction,
)
from ....struct import ObjectPosition
from .....utils.class_registry import register_class
from ....summon.base import AttackerSummonBase
from ....modifiable_values import DamageDecreaseValue
from ....match import Match
from ....event import (
    DeclareRoundEndEventArguments,
    GameStartEventArguments,
    RoundPrepareEventArguments,
)
from ....status.character_status.base import DefendCharacterStatus
from ....struct import Cost
from ....consts import (
    CostLabels,
    DamageElementalType,
    DieColor,
    ElementType,
    FactionType,
    ObjectPositionType,
    WeaponType,
)
from ....character.character_base import (
    CharacterBase,
    CreateStatusPassiveSkill,
    ElementalBurstBase,
    ElementalSkillBase,
    PhysicalNormalAttackBase,
    TalentBase,
)
from .....utils.desc_registry import DescDictType


class FontemerPearl_4_4(DefendCharacterStatus):
    name: Literal["Fontemer Pearl"] = "Fontemer Pearl"
    desc: Literal["", "talent"] = ""
    version: Literal["4.4"] = "4.4"
    usage: int = 1
    max_usage: int = 1
    min_damage_to_trigger: int = 1
    max_in_one_time: int = 1

    extra_usage: int = 1
    round_extra_usage: int = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # if marked as talent, increase extra usage.
        if self.desc == "talent":
            self.extra_usage = 2
            self.round_extra_usage = 2

    def renew(self, obj: "FontemerPearl_4_4") -> None:
        # When renew, update extra usage. If has talent, update desc
        self.usage = max(self.usage, obj.usage)
        self.extra_usage = max(self.extra_usage, obj.extra_usage)
        self.round_extra_usage = max(self.round_extra_usage, obj.round_extra_usage)
        if obj.desc == "talent":
            self.desc = "talent"

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Match
    ) -> List[Actions]:
        self.extra_usage = self.round_extra_usage
        return []

    def value_modifier_DAMAGE_DECREASE(
        self, value: DamageDecreaseValue, match: Match, mode: Literal["TEST", "REAL"]
    ) -> DamageDecreaseValue:
        initial_usage = self.usage
        ret = super().value_modifier_DAMAGE_DECREASE(value, match, mode)
        if (
            initial_usage > self.usage
            and value.position.area == ObjectPositionType.SUMMON
            and self.extra_usage > 0
        ):
            # When damage from summon and usage decreased and has extra usage
            self.usage += 1
            self.extra_usage -= 1
        return ret

    def event_handler_DECLARE_ROUND_END(
        self, event: DeclareRoundEndEventArguments, match: Any
    ) -> List[DrawCardAction]:
        """
        if declare round end, draw card
        """
        if (
            match.player_tables[self.position.player_idx].active_character_idx
            == self.position.character_idx
            and event.action.player_idx == self.position.player_idx
        ):
            # active character
            return [
                DrawCardAction(
                    player_idx=self.position.player_idx,
                    number=1,
                    draw_if_filtered_not_enough=True,
                )
            ]
        return []


class ResonantCoralOrb_4_4(AttackerSummonBase):
    name: Literal["Resonant Coral Orb"] = "Resonant Coral Orb"
    version: Literal["4.4"] = "4.4"
    damage: int = 1
    damage_elemental_type: DamageElementalType = DamageElementalType.ELECTRO
    usage: int = 2
    max_usage: int = 2


class SwirlingSchoolOfFish(ElementalSkillBase):
    name: Literal["Swirling School of Fish"] = "Swirling School of Fish"
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(elemental_dice_color=DieColor.ELECTRO, elemental_dice_number=3)

    def get_actions(self, match: Match) -> List[Actions]:
        ret = super().get_actions(match)
        damage_action = ret[0]
        assert damage_action.type == ActionTypes.MAKE_DAMAGE
        status = (
            match.player_tables[self.position.player_idx]
            .characters[self.position.character_idx]
            .status
        )
        target_status = None
        for s in status:
            if s.name == "Fontemer Pearl":
                target_status = s
                break
        # if no status, only attack
        if target_status is None:
            return ret
        return ret + [
            ChangeObjectUsageAction(
                object_position=target_status.position, change_usage=1
            )
        ]


class FontemerHoarthunder(ElementalBurstBase):
    name: Literal["Fontemer Hoarthunder"] = "Fontemer Hoarthunder"
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color=DieColor.ELECTRO, elemental_dice_number=3, charge=2
    )

    def get_actions(self, match: Match) -> List[Actions]:
        args: Dict[str, Any] = {"usage": 2}
        if self.is_talent_equipped(match):
            args["desc"] = "talent"
        return super().get_actions(match) + [
            self.create_character_status("Fontemer Pearl", args),
            self.create_summon("Resonant Coral Orb"),
        ]


class PearlArmor(CreateStatusPassiveSkill):
    name: Literal["Pearl Armor"] = "Pearl Armor"
    status_name: Literal["Fontemer Pearl"] = "Fontemer Pearl"
    regenerate_when_revive: bool = False

    def event_handler_GAME_START(
        self, event: GameStartEventArguments, match: Match
    ) -> List[CreateObjectAction]:
        """
        When game begin, gain status
        """
        return [self.create_character_status(self.status_name, {"usage": 2})]


class PearlSolidification_4_4(TalentBase):
    name: Literal["Pearl Solidification"]
    version: Literal["4.4"] = "4.4"
    character_name: Literal["Millennial Pearl Seahorse"] = "Millennial Pearl Seahorse"
    cost: Cost = Cost()
    cost_label: int = (
        CostLabels.CARD.value | CostLabels.TALENT.value | CostLabels.EQUIPMENT.value
    )
    remove_when_used: bool = False

    def get_actions(self, target: ObjectPosition | None, match: Match) -> List[Actions]:
        assert target is not None
        ret = super().get_actions(target, match)
        # create status again, so it will be updated to talent version
        ret += [
            CreateObjectAction(
                object_name="Fontemer Pearl",
                object_position=target.set_area(ObjectPositionType.CHARACTER_STATUS),
                object_arguments={"desc": "talent"},
            )
        ]
        status = (
            match.player_tables[target.player_idx]
            .characters[target.character_idx]
            .status
        )
        pearl_status = None
        for s in status:
            if s.name == "Fontemer Pearl":
                pearl_status = s
                break
        if pearl_status is not None:
            # status already existed, increase usage
            ret += [
                ChangeObjectUsageAction(
                    object_position=pearl_status.position, change_usage=1
                )
            ]
        return ret


class MillennialPearlSeahorse_4_4(CharacterBase):
    name: Literal["Millennial Pearl Seahorse"]
    version: Literal["4.4"] = "4.4"
    element: ElementType = ElementType.ELECTRO
    max_hp: int = 8
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase
        | SwirlingSchoolOfFish
        | FontemerHoarthunder
        | PearlArmor
    ] = []
    faction: List[FactionType] = [FactionType.MONSTER]
    weapon_type: WeaponType = WeaponType.OTHER

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name="Tail Sweep",
                cost=PhysicalNormalAttackBase.get_cost(self.element),
            ),
            SwirlingSchoolOfFish(),
            FontemerHoarthunder(),
            PearlArmor(),
        ]


desc: Dict[str, DescDictType] = {
    "CHARACTER/Millennial Pearl Seahorse": {
        "names": {"en-US": "Millennial Pearl Seahorse", "zh-CN": "千年珍珠骏麟"},
        "descs": {"4.4": {"en-US": "", "zh-CN": ""}},
        "image_path": "cardface/Char_Monster_SeaHorsePrimo.png",  # noqa: E501
        "id": 2403,
    },
    "SKILL_Millennial Pearl Seahorse_NORMAL_ATTACK/Tail Sweep": {
        "names": {"en-US": "Tail Sweep", "zh-CN": "旋尾扇击"},
        "descs": {
            "4.4": {"en-US": "Deals 2 Physical DMG.", "zh-CN": "造成2点物理伤害。"}
        },
    },
    "SKILL_Millennial Pearl Seahorse_ELEMENTAL_SKILL/Swirling School of Fish": {  # noqa: E501
        "names": {"en-US": "Swirling School of Fish", "zh-CN": "霰舞鱼群"},
        "descs": {
            "4.4": {
                "en-US": "Deals 3 Electro DMG. Once per Round: If this character has Fontemer Pearl attached, that Usage(s) +1.",  # noqa: E501
                "zh-CN": "造成3点雷元素伤害。\n每回合1次：如果本角色已附属原海明珠，则使其可用次数+1。",  # noqa: E501
            }
        },
    },
    "CHARACTER_STATUS/Fontemer Pearl": {
        "names": {"en-US": "Fontemer Pearl", "zh-CN": "原海明珠"},
        "descs": {
            "4.4": {
                "en-US": "When the character to which this is attached takes DMG: Negate 1 DMG. Once per Round, Usage(s) will not be used when negating DMG from Summons.\nUsage(s): 2\nWhen you declare the end of your Round: If the character to which this is attached is the active character, draw 1 card.",  # noqa: E501
                "zh-CN": "所附属角色受到伤害时：抵消1点伤害；每回合1次，抵消来自召唤物的伤害时不消耗可用次数。\n可用次数：2\n\n我方宣布结束时：如果所附属角色为「出战角色」，则抓1张牌。",  # noqa: E501
            }
        },
    },
    "CHARACTER_STATUS/Fontemer Pearl_talent": {
        "names": {"en-US": "Fontemer Pearl", "zh-CN": "原海明珠"},
        "descs": {
            "4.4": {
                "en-US": "When the character to which this is attached takes DMG: Negate 1 DMG. Twice per Round, Usage(s) will not be used when negating DMG from Summons.\nUsage(s): 2\nWhen you declare the end of your Round: If the character to which this is attached is the active character, draw 1 card.",  # noqa: E501
                "zh-CN": "所附属角色受到伤害时：抵消1点伤害；每回合2次，抵消来自召唤物的伤害时不消耗可用次数。\n可用次数：2\n\n我方宣布结束时：如果所附属角色为「出战角色」，则抓1张牌。",  # noqa: E501
            }
        },
    },
    "SKILL_Millennial Pearl Seahorse_ELEMENTAL_BURST/Fontemer Hoarthunder": {
        "names": {"en-US": "Fontemer Hoarthunder", "zh-CN": "原海古雷"},
        "descs": {
            "4.4": {
                "en-US": "Deals 1 Electro DMG, attaches Fontemer Pearl to this character, and summons 1 Resonant Coral Orb.",  # noqa: E501
                "zh-CN": "造成1点雷元素伤害，本角色附属原海明珠，召唤共鸣珊瑚珠。",  # noqa: E501
            }
        },
    },
    "SUMMON/Resonant Coral Orb": {
        "names": {"en-US": "Resonant Coral Orb", "zh-CN": "共鸣珊瑚珠"},
        "descs": {
            "4.4": {
                "en-US": "End Phase: Deal 1 Electro DMG.\nUsage(s): 2",
                "zh-CN": "结束阶段：造成1点雷元素伤害。\n可用次数：2",
            }
        },
        "image_path": "cardface/Summon_SeaHorsePrimo.png",
    },
    "SKILL_Millennial Pearl Seahorse_PASSIVE/Pearl Armor": {
        "names": {"en-US": "Pearl Armor", "zh-CN": "明珠甲胄"},
        "descs": {
            "4.4": {
                "en-US": "(Passive) When the battle begins, attach Fontemer Pearl to this character.",  # noqa: E501
                "zh-CN": "【被动】战斗开始时，本角色附属原海明珠。",  # noqa: E501
            }
        },
    },
    "TALENT_Millennial Pearl Seahorse/Pearl Solidification": {
        "names": {"en-US": "Pearl Solidification", "zh-CN": "明珠固化"},
        "descs": {
            "4.4": {
                "en-US": "Can only be played if your active character is Millennial Pearl Seahorse: When entering play, Millennial Pearl Seahorse will have Fontemer Pearl with 1 Usage(s) attached to them. If they already have Fontemer Pearl attached, Usage(s) +1 instead.\nWhen the Fontemer Pearl attached to Millennial Pearl Seahorse negates DMG from Summons, change to Usage(s) not being consumed twice per Round.\n(Your deck must contain Millennial Pearl Seahorse to add this card to your deck)",  # noqa: E501
                "zh-CN": "我方出战角色为千年珍珠骏麟时，才能打出：入场时，使千年珍珠骏麟附属可用次数为1的原海明珠；如果已附属原海明珠，则使其可用次数+1。\n装备有此牌的千年珍珠骏麟所附属的原海明珠抵消召唤物伤害时，改为每回合2次不消耗可用次数。\n（牌组中包含千年珍珠骏麟，才能加入牌组）",  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Talent_SeaHorsePrimo.png",  # noqa: E501
        "id": 224031,
    },
}


register_class(
    FontemerPearl_4_4
    | ResonantCoralOrb_4_4
    | MillennialPearlSeahorse_4_4
    | PearlSolidification_4_4,
    desc,
)
