# TODO: cicin usage 2 get hutao should disappear
from typing import Any, Dict, List, Literal

from pydantic import PrivateAttr


from lpsim.server.character.cryo.fatui_cryo_cicin_mage_4_1 import CryoCicins_4_1
from lpsim.server.consts import IconType, PlayerActionLabels
from lpsim.server.status.character_status.base import PrepareCharacterStatus
from lpsim.server.status.team_status.base import ShieldTeamStatus, TeamStatusBase
from lpsim.utils.class_registry import register_class
from lpsim.server.match import Match
from lpsim.utils.desc_registry import DescDictType
from lpsim.server.modifiable_values import DamageValue
from lpsim.server.event import (
    ActionEndEventArguments,
    PlayerActionStartEventArguments,
    RemoveObjectEventArguments,
    RoundPrepareEventArguments,
    SkillEndEventArguments,
)
from lpsim.server.action import (
    ActionTypes,
    Actions,
    ChangeObjectUsageAction,
    CreateObjectAction,
    MakeDamageAction,
    RemoveObjectAction,
)
from lpsim.server.struct import Cost, ObjectPosition
from lpsim.consts import (
    ELEMENT_TO_DAMAGE_TYPE,
    DamageElementalType,
    DamageType,
    DieColor,
    ElementType,
    FactionType,
    ObjectPositionType,
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


class ElectroCicinShield_4_5(ShieldTeamStatus):
    name: Literal["Electro Cicin Shield"] = "Electro Cicin Shield"
    version: Literal["4.5"] = "4.5"
    usage: int = 1
    max_usage: int = 1


# Team status.


class ElectroCicinStatus_4_5(TeamStatusBase):
    name: Literal["Electro Cicin"] = "Electro Cicin"
    version: Literal["4.5"] = "4.5"
    usage: int = 0
    max_usage: int = 3
    icon_type: IconType = IconType.DEBUFF

    def event_handler_ACTION_END(
        self, event: ActionEndEventArguments, match: Match
    ) -> List[ChangeObjectUsageAction]:
        """
        When play 3 cards, increase usage
        """
        if (
            event.action.position.player_idx != self.position.player_idx
            or event.action.action_label & PlayerActionLabels.CARD.value == 0
        ):
            # not self player, or not use card
            return []
        self.usage = min(self.max_usage, self.usage + 1)
        if self.usage != self.max_usage:
            return []
        cicin = self.query_one(match, 'opponent summon name="Electro Cicin"')
        assert cicin is not None
        if cicin.usage == 3:  # type: ignore
            # when cicin already full, not increase
            return []
        # increase cicin usage
        self.usage = 0
        return [ChangeObjectUsageAction(object_position=cicin.position, change_usage=1)]

    def event_handler_REMOVE_OBJECT(
        self, event: RemoveObjectEventArguments, match: Match
    ) -> List[RemoveObjectAction]:
        """
        when opposite cicin removed, remove self
        """
        if (
            self.position.not_satisfy(
                "both pidx=diff and target area=summon",
                target=event.action.object_position,
            )
            or event.object_name != "Electro Cicin"
        ):
            # not remove opposite electro cicin
            return []
        return [RemoveObjectAction(object_position=self.position)]


class SurgingThunderStatus_4_5(PrepareCharacterStatus):
    name: Literal["Surging Thunder"] = "Surging Thunder"
    version: Literal["4.5"] = "4.5"
    character_name: Literal["Fatui Electro Cicin Mage"] = "Fatui Electro Cicin Mage"
    skill_name: Literal["Surging Thunder"] = "Surging Thunder"


# Summons


class ElectroCicin_4_5(CryoCicins_4_1):
    name: Literal["Electro Cicin"] = "Electro Cicin"
    version: Literal["4.5"] = "4.5"
    usage: int = 3
    max_usage: int = 3
    damage_elemental_type: DamageElementalType = DamageElementalType.ELECTRO
    damage: int = 1
    _character_name: Literal["Fatui Electro Cicin Mage"] = PrivateAttr(
        "Fatui Electro Cicin Mage"
    )

    def renew(self, new_status: "ElectroCicin_4_5") -> None:
        # cryo cicin will over maximum, but electro will never.
        self.over_maximum = False
        return super().renew(new_status)

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[Actions]:
        # after skill end will do nothing
        return []


# Skills


class MistyCall(ElementalSkillBase):
    name: Literal["Misty Call"] = "Misty Call"
    damage: int = 0
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(elemental_dice_color=DieColor.ELECTRO, elemental_dice_number=3)

    def get_actions(self, match: Match) -> List[Actions]:
        """
        Attack and create object
        """
        return [
            self.create_summon("Electro Cicin"),
            CreateObjectAction(
                object_name="Electro Cicin",
                object_position=ObjectPosition(
                    player_idx=1 - self.position.player_idx,
                    area=ObjectPositionType.TEAM_STATUS,
                    id=-1,
                ),
                object_arguments={},
            ),
            self.charge_self(1),
        ]


class ThunderingShield(ElementalBurstBase):
    name: Literal["Thundering Shield"] = "Thundering Shield"
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color=DieColor.ELECTRO, elemental_dice_number=3, charge=2
    )

    def get_actions(self, match: Match) -> List[Actions]:
        ret = super().get_actions(match)
        damage_action = ret[1]
        assert damage_action.type == ActionTypes.MAKE_DAMAGE
        sc = self.query_one(match, "self")
        assert sc is not None
        damage_action.damage_value_list.append(
            DamageValue.create_element_application(
                self.position,
                sc.position,
                element=DamageElementalType.ELECTRO,
                cost=self.cost,
            )
        )
        shield_args = {
            "usage": 1,
            "max_usage": 1,
        }
        cicin = self.query_one(match, 'our summon name="Electro Cicin"')
        if cicin is not None:
            usage = cicin.usage  # type: ignore
            shield_args["usage"] = 1 + usage
            shield_args["max_usage"] = 1 + usage
        ret.append(self.create_team_status("Electro Cicin Shield", shield_args))
        ret.append(self.create_character_status("Surging Thunder"))
        return ret


class SurgingThunder(ElementalBurstBase):
    name: Literal["Surging Thunder"] = "Surging Thunder"
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost()

    def is_valid(self, match: Match) -> bool:
        """
        Always invalid for prepare skills
        """
        return False


# Talents


class ElectroCicinsGleam_4_5(SkillTalent):
    name: Literal["Electro Cicin's Gleam"]
    version: Literal["4.5"] = "4.5"
    character_name: Literal["Fatui Electro Cicin Mage"] = "Fatui Electro Cicin Mage"
    cost: Cost = Cost(elemental_dice_color=DieColor.ELECTRO, elemental_dice_number=3)
    skill: Literal["Misty Call"] = "Misty Call"
    usage: int = 1

    def get_actions(self, target: ObjectPosition | None, match: Any) -> List[Actions]:
        self.usage = 1
        return super().get_actions(target, match)

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Match
    ) -> List[Actions]:
        self.usage = 1
        return []

    def event_handler_PLAYER_ACTION_START(
        self, event: PlayerActionStartEventArguments, match: Match
    ) -> List[MakeDamageAction | ChangeObjectUsageAction]:
        # TODO: in game, when multiple talent exist, all of them trigger when condition
        # satisfied. Implement here will cause only one talent trigger, may move to
        # cicin.
        if self.usage == 0:
            return []
        if self.position.not_satisfy(f"source area=character pidx={event.player_idx}"):
            # not equipped, or not self start
            return []
        cicin: ElectroCicin_4_5 = self.query_one(
            match, 'our summon name="Electro Cicin"'
        )  # type: ignore
        if cicin is None or cicin.usage < 3:
            # no cicin or usage not full
            return []
        # attack and decrease usage
        target = self.query_one(match, "opponent active")
        assert target is not None
        self.usage -= 1
        return [
            MakeDamageAction(
                damage_value_list=[
                    DamageValue(
                        position=cicin.position,
                        damage_type=DamageType.DAMAGE,
                        target_position=target.position,
                        damage=cicin.damage,
                        damage_elemental_type=cicin.damage_elemental_type,
                        cost=Cost(),
                    )
                ]
            ),
            ChangeObjectUsageAction(object_position=cicin.position, change_usage=-1),
        ]


# character base


# character class name should contain its version.
class FatuiElectroCicinMage_4_5(CharacterBase):
    name: Literal["Fatui Electro Cicin Mage"]
    version: Literal["4.5"] = "4.5"
    element: ElementType = ElementType.ELECTRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        ElementalNormalAttackBase | MistyCall | ThunderingShield | SurgingThunder
    ] = []
    faction: List[FactionType] = [FactionType.MONSTER]
    weapon_type: WeaponType = WeaponType.OTHER

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name="Hurtling Bolts",
                damage_type=ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost=ElementalNormalAttackBase.get_cost(self.element),
            ),
            MistyCall(),
            ThunderingShield(),
            SurgingThunder(),
        ]


# define descriptions of newly defined classes. Note key of skills and talents
# have character names. For balance changes, only descs are needed to define.
character_descs: Dict[str, DescDictType] = {
    "CHARACTER/Fatui Electro Cicin Mage": {
        "names": {"en-US": "Fatui Electro Cicin Mage", "zh-CN": "愚人众·雷萤术士"},
        "descs": {"4.5": {"en-US": "", "zh-CN": ""}},
        "image_path": "cardface/Char_Monster_FatuusSummoner.png",  # noqa: E501
        "id": 2404,
    },
    "SKILL_Fatui Electro Cicin Mage_NORMAL_ATTACK/Hurtling Bolts": {
        "names": {"en-US": "Hurtling Bolts", "zh-CN": "轰闪落雷"},
        "descs": {
            "4.5": {"en-US": "Deals 1 Electro DMG.", "zh-CN": "造成1点雷元素伤害。"}
        },
    },
    "SKILL_Fatui Electro Cicin Mage_ELEMENTAL_SKILL/Misty Call": {
        "names": {"en-US": "Misty Call", "zh-CN": "雾虚之召"},
        "descs": {"4.5": {"en-US": "Summons 1 Electro Cicin.", "zh-CN": "召唤雷萤。"}},
    },
    "TEAM_STATUS/Electro Cicin": {
        "names": {"en-US": "Electro Cicin", "zh-CN": "雷萤"},
        "descs": {
            "4.5": {
                "en-US": "After you play a total of 3 Action Cards: Your opponent's Electro Cicin gains 1 Usage(s).",  # noqa: E501
                "zh-CN": "我方累计打出3张行动牌后：敌方雷萤可用次数+1。",
            }
        },
    },
    "SUMMON/Electro Cicin": {
        "names": {"en-US": "Electro Cicin", "zh-CN": "雷萤"},
        "descs": {
            "4.5": {
                "en-US": "End Phase: Deal 1 Electro DMG.\nUsage(s): 3\n\nAfter your opponent plays a total of 3 Action Cards: This card gains 1 Usage(s). (Max 3 stacks)\nAfter Fatui Electro Cicin Mage takes Elemental Reaction DMG: This card loses 1 Usage(s).",  # noqa: E501
                "zh-CN": "结束阶段：造成1点雷元素伤害。\n可用次数：3\n\n敌方累计打出3张行动牌后：此牌可用次数+1。（最多叠加到3）\n愚人众·雷萤术士受到元素反应伤害后：此牌可用次数-1。",  # noqa: E501
            }
        },
        "image_path": "cardface/Summon_FatuusSummoner.png",
    },
    "SKILL_Fatui Electro Cicin Mage_ELEMENTAL_BURST/Thundering Shield": {
        "names": {"en-US": "Thundering Shield", "zh-CN": "霆雷之护"},
        "descs": {
            "4.5": {
                "en-US": "Deals 1 Electro DMG, applies Electro Application to this character, creates 1 Electro Cicin Shield and prepares Surging Thunder.",  # noqa: E501
                "zh-CN": "造成1点雷元素伤害，本角色附着雷元素，生成雷萤护罩并准备技能霆电迸发。",  # noqa: E501
            }
        },
    },
    "TEAM_STATUS/Electro Cicin Shield": {
        "names": {"en-US": "Electro Cicin Shield", "zh-CN": "雷萤护罩"},
        "descs": {
            "4.5": {
                "en-US": "Shield\nProvides 1 Shield point for your active character.\nWhen created: If you have Electro Cicin on the field, additionally increase Shield by the amount of Usage(s) it has. (Adds a maximum of 3 additional Shield)",  # noqa: E501
                "zh-CN": "护盾\n为我方出战角色提供1点护盾。\n创建时：如果我方场上存在雷萤，则额外提供其可用次数的护盾。（最多额外提供3点护盾）",  # noqa: E501
            }
        },
    },
    "CHARACTER_STATUS/Surging Thunder": {
        "names": {"en-US": "Surging Thunder", "zh-CN": "霆电迸发"},
        "descs": {
            "4.5": {
                "en-US": "Elemental Burst\n(Prepare for 1 turn)\nDeals 2 Electro DMG.",
                "zh-CN": "元素爆发\n（需准备1个行动轮）\n造成2点雷元素伤害。",
            }
        },
    },
    "SKILL_Fatui Electro Cicin Mage_ELEMENTAL_BURST/Surging Thunder": {
        "names": {"en-US": "Surging Thunder", "zh-CN": "霆电迸发"},
        "descs": {
            "4.5": {
                "en-US": "(Prepare for 1 turn)\nDeals 2 Electro DMG.",
                "zh-CN": "（需准备1个行动轮）\n造成2点雷元素伤害。",
            }
        },
    },
    "TALENT_Fatui Electro Cicin Mage/Electro Cicin's Gleam": {
        "names": {"en-US": "Electro Cicin's Gleam", "zh-CN": "雷萤浮闪"},
        "descs": {
            "4.5": {
                "en-US": "Combat Action: When your active character is Fatui Electro Cicin Mage, equip this card.\nAfter Fatui Electro Cicin Mage equips this card, immediately use Misty Call once.\nIf your Fatui Electro Cicin Mage who has this card equipped is on the field, before you choose an action: If Electro Cicin's Usage(s) is at least 3, then Electro Cicin will immediately deal 1 Electro DMG. (Usage(s) will be consumed, once per Round)\n(You must have Fatui Electro Cicin Mage in your deck to add this card to your deck.)",  # noqa: E501
                "zh-CN": "战斗行动：我方出战角色为愚人众·雷萤术士时，装备此牌。\n愚人众·雷萤术士装备此牌后，立刻使用一次雾虚之召。\n装备有此牌的愚人众·雷萤术士在场时，我方选择行动前：如果雷萤的可用次数至少为3，则雷萤立刻造成1点雷元素伤害。（需消耗可用次数，每回合1次）\n（牌组中包含愚人众·雷萤术士，才能加入牌组）",  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Talent_FatuusSummoner.png",  # noqa: E501
        "id": 224041,
    },
}


register_class(
    FatuiElectroCicinMage_4_5
    | ElectroCicin_4_5
    | ElectroCicinShield_4_5
    | ElectroCicinStatus_4_5
    | ElectroCicinsGleam_4_5
    | SurgingThunderStatus_4_5,
    character_descs,
)
