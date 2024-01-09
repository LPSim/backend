from typing import Dict, List, Literal

from .....utils.class_registry import register_class

from ....action import Actions, ChangeObjectUsageAction, DrawCardAction

from ....status.team_status.base import ExtraAttackTeamStatus, RoundTeamStatus
from ....modifiable_values import (
    DamageElementEnhanceValue, InitialDiceColorValue
)
from ....event import RoundEndEventArguments, SkillEndEventArguments
from ....status.charactor_status.base import ElementalInfusionCharactorStatus
from ....match import Match
from ....struct import Cost
from ....consts import (
    DamageElementalType, DieColor, ElementType, FactionType, IconType, 
    ObjectPositionType, SkillType, WeaponType 
)
from ....charactor.charactor_base import (
    CharactorBase, CreateStatusPassiveSkill, ElementalBurstBase, 
    ElementalSkillBase, PhysicalNormalAttackBase, SkillTalent
)
from .....utils.desc_registry import DescDictType


class BreakthroughStatus_4_3(ElementalInfusionCharactorStatus):
    """
    Adding usage ways:
    1. when create, it contains 1.
    2. when renew, it adds 1 (by ADD renew_type)
    3. added by elemental skill (by skill add usage action)
    4. added in round end
    """
    name: Literal['Breakthrough'] = 'Breakthrough'
    version: Literal['4.3'] = '4.3'
    usage: int = 1
    max_usage: int = 3
    infused_elemental_type: ElementType = ElementType.HYDRO
    icon_type: Literal[
        IconType.ELEMENT_ENCHANT_WATER] = IconType.ELEMENT_ENCHANT_WATER

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Match
    ) -> List[Actions]:
        self.usage = min(self.usage + 1, self.max_usage)
        return []

    def value_modifier_DAMAGE_ELEMENT_ENHANCE(
        self, value: DamageElementEnhanceValue, match: Match,
        mode: Literal['TEST', 'REAL']
    ) -> DamageElementEnhanceValue:
        if self.usage < 2:
            # usage not enough, not modify
            return value
        return super().value_modifier_DAMAGE_ELEMENT_ENHANCE(
            value, match, mode)

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Match
    ) -> List[DrawCardAction]:
        """
        If self use normal attack and have usage, (it should be enhanced),
        draw a card.
        """
        if self.usage < 2:
            # usage not enough, not modify
            return []
        if (
            event.action.skill_type != SkillType.NORMAL_ATTACK
            or event.action.position.player_idx != self.position.player_idx
            or event.action.position.charactor_idx
            != self.position.charactor_idx
        ):
            # not self use normal attack
            return []
        # decrease usage and draw a card
        self.usage -= 2
        return [DrawCardAction(
            player_idx = self.position.player_idx,
            number = 1,
            draw_if_filtered_not_enough = True
        )]


class ExquisiteThrow_4_3(ExtraAttackTeamStatus, RoundTeamStatus):
    name: Literal['Exquisite Throw'] = 'Exquisite Throw'
    version: Literal['4.3'] = '4.3'
    damage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.HYDRO
    usage: int = 2
    max_usage: int = 2
    decrease_usage: bool = False
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS
    trigger_skill_type: SkillType = SkillType.NORMAL_ATTACK


class LingeringLifeline(ElementalSkillBase):
    name: Literal['Lingering Lifeline'] = 'Lingering Lifeline'
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Match) -> List[Actions]:
        status = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx].status
        for s in status:
            if s.name == 'Breakthrough':  # pragma: no branch
                break_through = s
                break
        else:
            raise AssertionError('Breakthrough not found')
        return super().get_actions(match) + [
            ChangeObjectUsageAction(
                object_position = break_through.position,
                change_usage = 2,
                max_usage = break_through.max_usage,
            )
        ]


class DepthClarionDice(ElementalBurstBase):
    name: Literal['Depth-Clarion Dice'] = 'Depth-Clarion Dice'
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3,
        charge = 3,
    )

    def get_actions(self, match: Match) -> List[Actions]:
        return super().get_actions(match, [
            self.create_team_status('Exquisite Throw'),
        ])


class Breakthrough(CreateStatusPassiveSkill):
    name: Literal['Breakthrough'] = 'Breakthrough'
    status_name: Literal['Breakthrough'] = 'Breakthrough'


class TurnControl_4_3(SkillTalent):
    name: Literal['Turn Control']
    version: Literal['4.3'] = '4.3'
    charactor_name: Literal['Yelan'] = 'Yelan'
    skill: Literal['Lingering Lifeline'] = 'Lingering Lifeline'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3,
    )

    def value_modifier_INITIAL_DICE_COLOR(
        self, value: InitialDiceColorValue, match: Match,
        mode: Literal['REAL', 'TEST']
    ) -> InitialDiceColorValue:
        """
        If equipped, add omni based on element type number.
        """
        if self.position.area != ObjectPositionType.CHARACTOR:
            # not equipped, not modify
            return value
        if value.player_idx != self.position.player_idx:
            # not self player, not modify
            return value
        charactors = match.player_tables[self.position.player_idx].charactors
        elements = set()
        for charactor in charactors:
            elements.add(charactor.element)
        # add omni based on element type number
        value.dice_colors += [DieColor.OMNI] * len(elements)
        return value


class Yelan_4_3(CharactorBase):
    name: Literal["Yelan"]
    version: Literal['4.3'] = '4.3'
    element: ElementType = ElementType.HYDRO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        PhysicalNormalAttackBase | LingeringLifeline | DepthClarionDice
        | Breakthrough
    ] = []
    faction: List[FactionType] = [FactionType.LIYUE]
    weapon_type: WeaponType = WeaponType.BOW

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Stealthy Bowshot',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            LingeringLifeline(),
            DepthClarionDice(),
            Breakthrough(),
        ]


desc: Dict[str, DescDictType] = {
    "CHARACTOR/Yelan": {
        "names": {
            "en-US": "Yelan",
            "zh-CN": "夜兰"
        },
        "image_path": "cardface/Char_Avatar_Yelan.png",  # noqa: E501
        "id": 1209,
        "descs": {
            "4.3": {
                "en-US": "",
                "zh-CN": ""
            },
        },
    },
    "SKILL_Yelan_NORMAL_ATTACK/Stealthy Bowshot": {
        "names": {
            "en-US": "Stealthy Bowshot",
            "zh-CN": "潜形隐曜弓"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 2 Physical DMG.",
                "zh-CN": "造成2点物理伤害。"
            }
        }
    },
    "SKILL_Yelan_ELEMENTAL_SKILL/Lingering Lifeline": {
        "names": {
            "en-US": "Lingering Lifeline",
            "zh-CN": "萦络纵命索"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 3 Hydro DMG. This character gains 2 Breakthrough stacks.",  # noqa: E501
                "zh-CN": "造成3点水元素伤害，此角色的破局层数+2。"
            }
        }
    },
    "CHARACTOR_STATUS/Breakthrough": {
        "names": {
            "en-US": "Breakthrough",
            "zh-CN": "破局"
        },
        "descs": {
            "4.3": {
                "en-US": "This state starts with 1 Breakthrough stack. When re-attached, add 1 Breakthrough stack. Breakthrough can have a maximum of 3 stacks.\nEnd Phase: Gain 1 Breakthrough stack.\n\nWhen the character to which this is attached performs a $[K51]: If possible, consume 2 Breakthrough stacks to convert Physical DMG dealt into Hydro DMG and draw 1 card.",  # noqa: E501
                "zh-CN": "此状态初始具有1层「破局」；重复附属时，叠加1层「破局」。「破局」最多可以叠加到3层。\n结束阶段：叠加1层「破局」。\n\n所附属角色普通攻击时：如可能，则消耗2层「破局」，使造成的物理伤害转换为水元素伤害，并抓1张牌。"  # noqa: E501
            }
        }
    },
    "SKILL_Yelan_ELEMENTAL_BURST/Depth-Clarion Dice": {
        "names": {
            "en-US": "Depth-Clarion Dice",
            "zh-CN": "渊图玲珑骰"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 1 Hydro DMG, creates 1 Exquisite Throw.",
                "zh-CN": "造成1点水元素伤害，生成玄掷玲珑。"
            }
        }
    },
    "TEAM_STATUS/Exquisite Throw": {
        "names": {
            "en-US": "Exquisite Throw",
            "zh-CN": "玄掷玲珑"
        },
        "descs": {
            "4.3": {
                "en-US": "After your character uses a Normal Attack: Deal 1 Hydro DMG. If the remaining Duration (Rounds) is only 1, this DMG increases by 1.\nDuration (Rounds): 2",  # noqa: E501
                "zh-CN": "我方角色普通攻击后：造成2点水元素伤害。\n持续回合：2"
            }
        },
        "image_path": "status/Yelan_E.png"
    },
    "SKILL_Yelan_PASSIVE/Breakthrough": {
        "names": {
            "en-US": "Breakthrough",
            "zh-CN": "破局"
        },
        "descs": {
            "4.3": {
                "en-US": "(Passive) When the battle begins, this character gains Breakthrough.",  # noqa: E501
                "zh-CN": "【被动】战斗开始时，初始附属破局。"
            }
        }
    },
    "TALENT_Yelan/Turn Control": {
        "names": {
            "en-US": "Turn Control",
            "zh-CN": "猜先有方"
        },
        "descs": {
            "4.3": {
                "en-US": "Combat Action: When your active character is Yelan, equip this card.\nAfter Yelan equips this card, immediately use Lingering Lifeline once.\nRoll Phase: If Yelan, who has this card equipped, is on the field, 1 Elemental Dice will be rolled as Omni Element for each Elemental Type in your party. (Max 3)\n(You must have Yelan in your deck to add this card to your deck.)",  # noqa: E501
                "zh-CN": "战斗行动：我方出战角色为夜兰时，装备此牌。\n夜兰装备此牌后，立刻使用一次萦络纵命索。\n投掷阶段：装备有此牌的夜兰在场，则我方队伍中每有1种元素类型，就使1个元素骰总是投出万能元素。（最多3个）\n（牌组中包含夜兰，才能加入牌组）"  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Talent_Yelan.png",  # noqa: E501
        "id": 212091
    },
}


register_class(
    BreakthroughStatus_4_3 | ExquisiteThrow_4_3 | TurnControl_4_3 | Yelan_4_3,
    desc
)
