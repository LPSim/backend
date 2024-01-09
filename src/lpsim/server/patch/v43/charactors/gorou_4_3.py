from typing import Dict, List, Literal

from ....status.team_status.base import RoundTeamStatus
from .....utils.class_registry import register_class
from ....action import (
    ActionTypes, Actions, ChangeObjectUsageAction, CreateObjectAction, 
    DrawCardAction, MakeDamageAction
)
from ....event import (
    RoundEndEventArguments, RoundPrepareEventArguments, SkillEndEventArguments
)
from ....summon.base import AttackerSummonBase
from ....modifiable_values import DamageIncreaseValue
from ....match import Match
from ....struct import Cost, ObjectPosition
from ....consts import (
    DamageElementalType, DamageType, DieColor, ElementType, FactionType, 
    IconType, ObjectPositionType, WeaponType
)
from ....charactor.charactor_base import (
    CharactorBase, ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, SkillTalent
)
from .....utils.desc_registry import DescDictType


class GeneralsWarBanner_4_3(RoundTeamStatus):
    name: Literal["General's War Banner"] = "General's War Banner"
    version: Literal['4.3'] = '4.3'
    usage: int = 2
    max_usage: int = 3

    icon_type: IconType = IconType.OTHERS

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Match,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        if (
            value.position.area != ObjectPositionType.SKILL
            and value.position.area != ObjectPositionType.CHARACTOR
        ):
            # not damage from charactor
            return value
        if value.position.player_idx != self.position.player_idx:
            # not damage from self
            return value
        if (
            value.damage_type != DamageType.DAMAGE
            or value.damage_elemental_type != DamageElementalType.GEO
        ):
            # not geo damage
            return value
        # increase damage
        assert mode == 'REAL'
        value.damage += 1
        return value


class GeneralsGlory_4_3(AttackerSummonBase):
    name: Literal["General's Glory"] = "General's Glory"
    version: Literal['4.3'] = '4.3'
    usage: int = 2
    max_usage: int = 2
    damage: int = 1
    damage_elemental_type: DamageElementalType = DamageElementalType.GEO

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Match
    ) -> List[MakeDamageAction | ChangeObjectUsageAction | CreateObjectAction]:
        ret: List[
            MakeDamageAction | ChangeObjectUsageAction | CreateObjectAction
        ] = []
        ret += super().event_handler_ROUND_END(event, match)
        damage_action = ret[0]
        assert damage_action.type == ActionTypes.MAKE_DAMAGE
        charactors = match.player_tables[self.position.player_idx].charactors
        geo_number = 0
        for charactor in charactors:
            if charactor.element == ElementType.GEO:
                geo_number += 1
        if geo_number >= 2:
            damage_action.create_objects.append(CreateObjectAction(
                object_name = 'Crystallize',
                object_position = ObjectPosition(
                    player_idx = self.position.player_idx,
                    area = ObjectPositionType.TEAM_STATUS,
                    id = -1
                ),
                object_arguments = {}
            ))
        return ret


class InuzakaAllRoundDefense(ElementalSkillBase):
    name: Literal["Inuzaka All-Round Defense"] = "Inuzaka All-Round Defense"
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.GEO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.GEO,
        elemental_dice_number = 3,
    )

    def get_actions(self, match: Match) -> List[Actions]:
        return super().get_actions(match, [
            self.create_team_status('General\'s War Banner')
        ])


class JuugaForwardUntoVictory(ElementalBurstBase):
    name: Literal[
        "Juuga: Forward Unto Victory"] = "Juuga: Forward Unto Victory"
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.GEO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.GEO,
        elemental_dice_number = 3,
        charge = 2
    )

    def get_actions(self, match: Match) -> List[Actions]:
        return super().get_actions(match, [
            self.create_team_status('General\'s War Banner'),
            self.create_summon('General\'s Glory')
        ])


class RushingHoundSwiftAsTheWind_4_3(SkillTalent):
    name: Literal[
        "Rushing Hound: Swift as the Wind"
    ] = "Rushing Hound: Swift as the Wind"
    version: Literal['4.3'] = '4.3'
    charactor_name: Literal["Gorou"] = "Gorou"
    skill: Literal["Inuzaka All-Round Defense"] = "Inuzaka All-Round Defense"
    cost: Cost = Cost(
        elemental_dice_color = DieColor.GEO,
        elemental_dice_number = 3,
    )
    usage: int = 1
    draw_card: bool = False

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Match
    ) -> List[Actions]:
        """
        Reset draw_card_usage
        """
        self.usage = 1
        self.draw_card = False
        return []

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Match,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        if self.position.area != ObjectPositionType.CHARACTOR:
            # not equipped
            return value
        if (
            value.position.area != ObjectPositionType.SKILL
            and value.position.area != ObjectPositionType.CHARACTOR
        ):
            # not damage from charactor
            return value
        if value.position.player_idx != self.position.player_idx:
            # not damage from self
            return value
        if (
            value.damage_type != DamageType.DAMAGE
            or value.damage_elemental_type != DamageElementalType.GEO
        ):
            # not geo damage
            return value
        if self.usage <= 0:
            # no usage
            return value
        assert mode == 'REAL'
        self.draw_card = True
        return value

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Match
    ) -> List[DrawCardAction]:
        """
        If draw_card is True, and has General's War Banner in play,
        and has usage, draw a card and reset draw_card to False.
        """
        if not self.draw_card:
            return []
        self.draw_card = False
        team_status = match.player_tables[self.position.player_idx].team_status
        for status in team_status:
            if status.name == 'General\'s War Banner':
                break
        else:
            return []
        assert self.usage > 0
        self.usage -= 1
        return [DrawCardAction(
            player_idx = self.position.player_idx,
            number = 1,
            draw_if_filtered_not_enough = True
        )]


class Gorou_4_3(CharactorBase):
    name: Literal["Gorou"]
    version: Literal['4.3']
    element: ElementType = ElementType.GEO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | InuzakaAllRoundDefense 
        | JuugaForwardUntoVictory
    ] = []
    faction: List[FactionType] = [
        FactionType.INAZUMA
    ]
    weapon_type: WeaponType = WeaponType.BOW

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Ripping Fang Fletching',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            InuzakaAllRoundDefense(),
            JuugaForwardUntoVictory(),
        ]


desc: Dict[str, DescDictType] = {
    "CHARACTOR/Gorou": {
        "names": {
            "en-US": "Gorou",
            "zh-CN": "五郎"
        },
        "image_path": "cardface/Char_Avatar_Gorou.png",  # noqa: E501
        "id": 1606,
        "descs": {
            "4.3": {
                "en-US": "",
                "zh-CN": ""
            }
        }
    },
    "SKILL_Gorou_NORMAL_ATTACK/Ripping Fang Fletching": {
        "names": {
            "en-US": "Ripping Fang Fletching",
            "zh-CN": "呲牙裂扇箭"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 2 Physical DMG.",
                "zh-CN": "造成2点物理伤害。"
            }
        }
    },
    "SKILL_Gorou_ELEMENTAL_SKILL/Inuzaka All-Round Defense": {
        "names": {
            "en-US": "Inuzaka All-Round Defense",
            "zh-CN": "犬坂吠吠方圆阵"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 2 Geo DMG, creates 1 General's War Banner.",
                "zh-CN": "造成2点岩元素伤害，生成大将旗指物。"
            }
        }
    },
    "TEAM_STATUS/General's War Banner": {
        "names": {
            "en-US": "General's War Banner",
            "zh-CN": "大将旗指物"
        },
        "descs": {
            "4.3": {
                "en-US": "Your party's characters deal +1 Geo DMG.\nDuration (Rounds): 2 (Can stack, Can stack till 3 Rounds)",  # noqa: E501
                "zh-CN": "我方角色造成的岩元素伤害+1。\n持续回合：2（可叠加，最多叠加到3回合）"  # noqa: E501
            }
        },
        "image_path": "status/Gorou_E.png"
    },
    "SKILL_Gorou_ELEMENTAL_BURST/Juuga: Forward Unto Victory": {
        "names": {
            "en-US": "Juuga: Forward Unto Victory",
            "zh-CN": "兽牙逐突形胜战法"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 2 Geo DMG, creates 1 General's War Banner, summons General's Glory.",  # noqa: E501
                "zh-CN": "造成2点岩元素伤害，生成大将旗指物，召唤大将威仪。"
            }
        }
    },
    "SUMMON/General's Glory": {
        "names": {
            "en-US": "General's Glory",
            "zh-CN": "大将威仪"
        },
        "descs": {
            "4.3": {
                "en-US": "End Phase: Deal 1 Geo DMG. If your party has 2 Geo characters, create 1 Crystallize.\nUsage(s): 2",  # noqa: E501
                "zh-CN": "结束阶段：造成1点岩元素伤害；如果队伍中存在2名岩元素角色，则生成结晶。\n可用次数：2"  # noqa: E501
            }
        }
    },
    "TALENT_Gorou/Rushing Hound: Swift as the Wind": {
        "names": {
            "en-US": "Rushing Hound: Swift as the Wind",
            "zh-CN": "犬奔·疾如风"
        },
        "descs": {
            "4.3": {
                "en-US": "Combat Action: When your active character is Gorou, equip this card.\nAfter Gorou equips this card, immediately use Inuzaka All-Round Defense once.\nWhen your Gorou, who has this card equipped, is on the field, and after any of your characters deals Geo DMG: If General's War Banner is in play, draw 1 card. (Once per Round)\n(You must have Gorou in your deck to add this card to your deck.)",  # noqa: E501
                "zh-CN": "战斗行动：我方出战角色为五郎时，装备此牌。\n五郎装备此牌后，立刻使用一次犬坂吠吠方圆阵。\n装备有此牌的五郎在场时，我方角色造成岩元素伤害后：如果场上存在大将旗指物，抓1张牌。（每回合1次）\n（牌组中包含五郎，才能加入牌组）"  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Constellation_Gorou.png",  # noqa: E501
        "id": 216061
    },
}


register_class(
    GeneralsGlory_4_3 | GeneralsWarBanner_4_3 | RushingHoundSwiftAsTheWind_4_3 
    | Gorou_4_3, desc
)
