from typing import Any, Dict, List, Literal

from pydantic import PrivateAttr

from lpsim.server.consts import (
    CostLabels,
    IconType,
    ObjectPositionType,
    PlayerActionLabels,
)
from lpsim.server.match import Match
from lpsim.server.status.team_status.base import (
    ShieldTeamStatus,
    SwitchActionTeamStatus,
    UsageTeamStatus,
)
from lpsim.utils.class_registry import register_class
from lpsim.utils.desc_registry import DescDictType
from lpsim.server.modifiable_values import CostValue, DamageValue
from lpsim.server.event import ActionEndEventArguments, RoundPrepareEventArguments
from lpsim.server.action import (
    Actions,
    CreateObjectAction,
    DrawCardAction,
    MakeDamageAction,
)
from lpsim.server.struct import Cost, ObjectPosition
from lpsim.consts import (
    DamageElementalType,
    DamageType,
    DieColor,
    ElementType,
    FactionType,
    WeaponType,
)
from lpsim.server.character.character_base import (
    ElementalBurstBase,
    ElementalSkillBase,
    PhysicalNormalAttackBase,
    CharacterBase,
    SkillTalent,
)


# Team status.


class UrgentNekoParcel_4_5(SwitchActionTeamStatus):
    name: Literal["Urgent Neko Parcel"] = "Urgent Neko Parcel"
    version: Literal["4.5"] = "4.5"
    usage: int = 1
    max_usage: int = 1
    icon_type: IconType = IconType.OTHERS

    def _action(self, match: Match) -> List[MakeDamageAction | DrawCardAction]:
        self.usage -= 1
        target = self.query_one(match, "opponent active")
        assert target is not None
        return [
            MakeDamageAction(
                damage_value_list=[
                    DamageValue(
                        position=self.position,
                        damage_type=DamageType.DAMAGE,
                        target_position=target.position,
                        damage=1,
                        damage_elemental_type=DamageElementalType.DENDRO,
                        cost=Cost(),
                    )
                ]
            ),
            DrawCardAction(
                player_idx=self.position.player_idx,
                number=1,
                draw_if_filtered_not_enough=True,
            ),
        ]


class ShieldOfSafeTransport_4_5(ShieldTeamStatus):
    name: Literal["Shield of Safe Transport"] = "Shield of Safe Transport"
    version: Literal["4.5"] = "4.5"
    usage: int = 2
    max_usage: int = 2


class CatGrassCardamom_4_5(UsageTeamStatus):
    name: Literal["Cat Grass Cardamom"] = "Cat Grass Cardamom"
    version: Literal["4.5"] = "4.5"
    usage: int = 2
    max_usage: int = 2
    counter: int = 0
    icon_type: IconType = IconType.OTHERS

    def event_handler_ACTION_END(
        self, event: ActionEndEventArguments, match: Match
    ) -> List[MakeDamageAction]:
        if (
            event.action.position.player_idx != self.position.player_idx
            or event.action.action_label & PlayerActionLabels.CARD.value == 0
        ):
            # not self player, or not use card
            return []
        self.counter += 1
        if self.counter == 2:
            target = self.query_one(match, "our active")
            self.usage -= 1
            self.counter = 0
            assert target is not None
            return [
                MakeDamageAction(
                    damage_value_list=[
                        DamageValue(
                            position=self.position,
                            damage_type=DamageType.DAMAGE,
                            target_position=target.position,
                            damage=1,
                            damage_elemental_type=DamageElementalType.DENDRO,
                            cost=Cost(),
                        )
                    ]
                )
            ]
        return []


# Skills


class MeowteorKick(ElementalSkillBase):
    name: Literal["Meow-teor Kick"] = "Meow-teor Kick"
    damage: int = 0
    damage_type: DamageElementalType = DamageElementalType.DENDRO
    cost: Cost = Cost(elemental_dice_color=DieColor.DENDRO, elemental_dice_number=3)

    def get_actions(self, match: Match) -> List[Actions]:
        return [
            self.create_team_status("Urgent Neko Parcel"),
            self.create_team_status("Shield of Safe Transport"),
            self.charge_self(1),
        ]


class SecretArtSurpriseDispatch(ElementalBurstBase):
    name: Literal["Secret Art: Surprise Dispatch"] = "Secret Art: Surprise Dispatch"
    damage: int = 4
    damage_type: DamageElementalType = DamageElementalType.DENDRO
    cost: Cost = Cost(
        elemental_dice_color=DieColor.DENDRO, elemental_dice_number=3, charge=2
    )

    def get_actions(self, match: Match) -> List[Actions]:
        """
        Attack and create opposite
        """
        return super().get_actions(match) + [
            CreateObjectAction(
                object_name="Cat Grass Cardamom",
                object_position=ObjectPosition(
                    player_idx=1 - self.position.player_idx,
                    area=ObjectPositionType.TEAM_STATUS,
                    id=0,
                ),
                object_arguments={},
            )
        ]


# Talents


class CountlessSightsToSee_4_5(SkillTalent):
    name: Literal["Countless Sights to See"]
    version: Literal["4.5"] = "4.5"
    character_name: Literal["Kirara"] = "Kirara"
    cost: Cost = Cost(elemental_dice_color=DieColor.DENDRO, elemental_dice_number=3)
    skill: Literal["Meow-teor Kick"] = "Meow-teor Kick"

    usage: int = 1
    _usage_per_round: int = PrivateAttr(1)

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Match
    ) -> List[Actions]:
        self.usage = self._usage_per_round
        return []

    def get_actions(self, target: ObjectPosition | None, match: Any) -> List[Actions]:
        self.usage = self._usage_per_round
        return super().get_actions(target, match)

    def value_modifier_COST(
        self, value: CostValue, match: Match, mode: Literal["TEST", "REAL"]
    ) -> CostValue:
        if self.usage == 0:
            return value
        if value.cost.label & CostLabels.SWITCH_CHARACTER.value == 0:
            # not switch character
            return value
        if self.position.not_satisfy(
            "both pidx=same cidx=same and source active=true",
            value.position,
            match=match,
        ):
            # not cost from self character to others
            return value
        value.cost.decrease_cost(None)
        if mode == "REAL":
            self.usage -= 1
        return value


# character base


# character class name should contain its version.
class Kirara_4_5(CharacterBase):
    name: Literal["Kirara"]
    version: Literal["4.5"] = "4.5"
    element: ElementType = ElementType.DENDRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | MeowteorKick | SecretArtSurpriseDispatch
    ] = []
    faction: List[FactionType] = [FactionType.INAZUMA]
    weapon_type: WeaponType = WeaponType.SWORD

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name="Boxcutter",
                cost=PhysicalNormalAttackBase.get_cost(self.element),
            ),
            MeowteorKick(),
            SecretArtSurpriseDispatch(),
        ]


# define descriptions of newly defined classes. Note key of skills and talents
# have character names. For balance changes, only descs are needed to define.
character_descs: Dict[str, DescDictType] = {
    "CHARACTER/Kirara": {
        "names": {"en-US": "Kirara", "zh-CN": "绮良良"},
        "descs": {"4.5": {"en-US": "", "zh-CN": ""}},
        "image_path": "cardface/Char_Avatar_Momoka.png",  # noqa: E501
        "id": 1707,
    },
    "SKILL_Kirara_NORMAL_ATTACK/Boxcutter": {
        "names": {"en-US": "Boxcutter", "zh-CN": "箱纸切削术"},
        "descs": {
            "4.5": {"en-US": "Deals 2 Physical DMG.", "zh-CN": "造成2点物理伤害。"}
        },
    },
    "SKILL_Kirara_ELEMENTAL_SKILL/Meow-teor Kick": {
        "names": {"en-US": "Meow-teor Kick", "zh-CN": "呜喵町飞足"},
        "descs": {
            "4.5": {
                "en-US": "Creates 1 Urgent Neko Parcel and Shield of Safe Transport.",
                "zh-CN": "生成猫箱急件和安全运输护盾。",
            }
        },
    },
    "TEAM_STATUS/Urgent Neko Parcel": {
        "names": {"en-US": "Urgent Neko Parcel", "zh-CN": "猫箱急件"},
        "descs": {
            "4.5": {
                "en-US": "When Kirara is your active character, after you switch characters: Deal 1 Dendro DMG and draw 1 card.\nUsage(s): 1 (Can stack. Max 2 stacks.)",  # noqa: E501
                "zh-CN": "绮良良为出战角色时，我方切换角色后：造成1点草元素伤害，抓1张牌。\n可用次数：1（可叠加，最多叠加到2次）",  # noqa: E501
            }
        },
        "image_path": "status/Momoka_S.png",
    },
    "TEAM_STATUS/Shield of Safe Transport": {
        "names": {"en-US": "Shield of Safe Transport", "zh-CN": "安全运输护盾"},
        "descs": {
            "4.5": {
                "en-US": "Shield\nGrants 2 Shield points to your active character.",
                "zh-CN": "护盾\n为我方出战角色提供2点护盾。",
            }
        },
    },
    "SKILL_Kirara_ELEMENTAL_BURST/Secret Art: Surprise Dispatch": {
        "names": {"en-US": "Secret Art: Surprise Dispatch", "zh-CN": "秘法·惊喜特派"},
        "descs": {
            "4.5": {
                "en-US": "Deals 4 Dendro DMG, creates 1 Cat Grass Cardamom on the opponent's side of the field.",  # noqa: E501
                "zh-CN": "造成4点草元素伤害，在敌方场上生成猫草豆蔻。",
            }
        },
    },
    "TEAM_STATUS/Cat Grass Cardamom": {
        "names": {"en-US": "Cat Grass Cardamom", "zh-CN": "猫草豆蔻"},
        "descs": {
            "4.5": {
                "en-US": "After the side of the field that this card is on has played 2 Action Cards: Deal 1 Dendro DMG to the active character on that side.\nUsage(s): 2",  # noqa: E501
                "zh-CN": "所在阵营打出2张行动牌后：对所在阵营的出战角色造成1点草元素伤害。\n可用次数：2",  # noqa: E501
            }
        },
        "image_path": "status/Debuff_Momoka_E.png",
    },
    "TALENT_Kirara/Countless Sights to See": {
        "names": {"en-US": "Countless Sights to See", "zh-CN": "沿途百景会心"},
        "descs": {
            "4.5": {
                "en-US": "Combat Action: When your active character is Kirara, equip this card.\nAfter Kirara equips this card, immediately use Meow-teor Kick once.\nWhen your Kirara who has this card equipped is the active character, spend 1 less Elemental Die when switching characters. (Once per Round)\n(You must have Kirara in your deck to add this card to your deck.)",  # noqa: E501
                "zh-CN": "战斗行动：我方出战角色为绮良良时，装备此牌。\n绮良良装备此牌后，立刻使用一次呜喵町飞足。\n装备有此牌的绮良良为出战角色，我方进行「切换角色」行动时：少花费1个元素骰。（每回合1次）\n（牌组中包含绮良良，才能加入牌组）",  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Talent_Momoka.png",  # noqa: E501
        "id": 217071,
    },
}


register_class(
    Kirara_4_5
    | UrgentNekoParcel_4_5
    | ShieldOfSafeTransport_4_5
    | CatGrassCardamom_4_5
    | CountlessSightsToSee_4_5,
    character_descs,
)
