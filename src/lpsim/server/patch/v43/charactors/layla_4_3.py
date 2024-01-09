from typing import Dict, List, Literal

from .....utils.class_registry import register_class
from ....summon.base import AttackerSummonBase
from ....modifiable_values import DamageValue
from ....event import (
    AfterMakeDamageEventArguments, ChangeObjectUsageEventArguments, 
    RoundEndEventArguments, SkillEndEventArguments
)
from ....status.team_status.base import ShieldTeamStatus, TeamStatusBase
from ....struct import Cost
from ....action import (
    Actions, ChangeObjectUsageAction, CreateObjectAction, DrawCardAction, 
    MakeDamageAction
)
from ....match import Match
from ....consts import (
    DamageElementalType, DamageType, DieColor, ElementType, FactionType, 
    IconType, ObjectPositionType, WeaponType
)
from ....charactor.charactor_base import (
    CharactorBase, ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, SkillTalent
)
from .....utils.desc_registry import DescDictType


class CurtainOfSlumberShield_4_3(ShieldTeamStatus):
    name: Literal['Curtain of Slumber Shield'] = 'Curtain of Slumber Shield'
    version: Literal['4.3'] = '4.3'
    usage: int = 2
    max_usage: int = 2


class ShootingStar_4_3(TeamStatusBase):
    """
    Actions related on Shooting Star
    1. Create Shooting Star
    2. After using skill, gain 1 Night Star
    3. Recreate Shooting Star, gain 2 Night Star
    4. When max_usage reached, deal 1 Cryo DMG and clear usage
    5. When deal DMG, if has layla with talent, draw 1 card. (This is 
        performed by talent card)
    """
    name: Literal['Shooting Star'] = 'Shooting Star'
    version: Literal['4.3'] = '4.3'
    usage: int = 0
    max_usage: int = 4
    icon_type: IconType = IconType.OTHERS

    def renew(self, new_status: 'ShootingStar_4_3') -> None:
        """
        When renew, add two usage
        """
        self.usage = min(self.usage + 2, self.max_usage)

    def _make_damage_to_opposite_active_if_max_usage(
        self, match: Match
    ) -> List[MakeDamageAction]:
        """
        Deal 1 Cryo DMG to opposite active and reset usage if max usage reached
        """
        if self.usage < self.max_usage:
            # not reach max usage, return
            return []
        self.usage = 0
        target = match.player_tables[
            1 - self.position.player_idx].get_active_charactor()
        return [MakeDamageAction(
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.DAMAGE,
                    target_position = target.position,
                    damage = 1,
                    damage_elemental_type = DamageElementalType.CRYO,
                    cost = Cost()
                )
            ]
        )]

    def event_handler_CREATE_OBJECT(
        self, event: CreateObjectAction, match: Match
    ) -> List[MakeDamageAction]:
        return self._make_damage_to_opposite_active_if_max_usage(match)

    def event_handler_CHANGE_OBJECT_USAGE(
        self, event: ChangeObjectUsageEventArguments, match: Match
    ) -> List[MakeDamageAction]:
        return self._make_damage_to_opposite_active_if_max_usage(match)

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Match
    ) -> List[MakeDamageAction]:
        """
        When self charactor use skill, gain 1 Night Star and check if need to
        deal damage
        """
        ret: List[MakeDamageAction] = []
        ret += self._make_damage_to_opposite_active_if_max_usage(match)
        if event.action.position.player_idx == self.position.player_idx:
            # self charactor use skill, gain 1 Night Star
            self.usage = min(self.usage + 1, self.max_usage)
        return ret + self._make_damage_to_opposite_active_if_max_usage(match)


class CelestialDreamsphere_4_3(AttackerSummonBase):
    name: Literal['Celestial Dreamsphere'] = 'Celestial Dreamsphere'
    version: Literal['4.3'] = '4.3'
    usage: int = 2
    max_usage: int = 2
    damage: int = 1
    damage_elemental_type: DamageElementalType = DamageElementalType.CRYO

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Match
    ) -> List[MakeDamageAction | ChangeObjectUsageAction]:
        ret: List[MakeDamageAction | ChangeObjectUsageAction] = []
        ret += super().event_handler_ROUND_END(event, match)
        team_status = match.player_tables[self.position.player_idx].team_status
        for status in team_status:
            if status.name == 'Shooting Star':
                # Shooting Star exist, gain 1 Night Star
                ret.append(ChangeObjectUsageAction(
                    object_position = status.position,
                    change_usage = 1
                ))
                break
        return ret


class NightsOfFormalFocus(ElementalSkillBase):
    name: Literal['Nights of Formal Focus'] = 'Nights of Formal Focus'
    damage: int = 0
    damage_type: DamageElementalType = DamageElementalType.PIERCING
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Match) -> List[Actions]:
        """
        Generate shield and shooting star
        """
        return [
            self.create_team_status('Curtain of Slumber Shield'),
            self.create_team_status('Shooting Star'),
            self.charge_self(1),
        ]


class DreamOfTheStarStreamShaker(ElementalBurstBase):
    name: Literal[
        'Dream of the Star-Stream Shaker'
    ] = 'Dream of the Star-Stream Shaker'
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.CRYO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 3,
        charge = 2
    )

    def get_actions(self, match: Match) -> List[Actions]:
        return super().get_actions(match, [
            self.create_summon('Celestial Dreamsphere'),
        ])


class LightsRemit_4_3(SkillTalent):
    name: Literal['Light\'s Remit'] = 'Light\'s Remit'
    version: Literal['4.3'] = '4.3'
    charactor_name: Literal['Layla'] = 'Layla'
    skill: Literal['Nights of Formal Focus'] = 'Nights of Formal Focus'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 3
    )

    def event_handler_AFTER_MAKE_DAMAGE(
        self, event: AfterMakeDamageEventArguments, match: Match
    ) -> List[DrawCardAction]:
        """
        When equipped, self Shooting Star deal damage, draw 1 card
        """
        if self.position.area != ObjectPositionType.CHARACTOR:
            # not equiped, return
            return []
        if (
            self.position.player_idx 
            != event.damages[0].final_damage.position.player_idx
        ):
            # not self attack, return
            return []
        obj = match.get_object(event.damages[0].final_damage.position)
        if obj is None:  # pragma: no cover
            # obj is None, return
            return []
        if obj.name != 'Shooting Star':
            # not Shooting Star, return
            return []
        # self Shooting Star deal damage, draw 1 card
        return [DrawCardAction(
            player_idx = self.position.player_idx,
            number = 1,
            draw_if_filtered_not_enough = True
        )]


class Layla_4_3(CharactorBase):
    name: Literal["Layla"]
    version: Literal['4.3'] = '4.3'
    element: ElementType = ElementType.CRYO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | NightsOfFormalFocus 
        | DreamOfTheStarStreamShaker
    ] = []
    faction: List[FactionType] = [FactionType.SUMERU]
    weapon_type: WeaponType = WeaponType.SWORD

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Sword of the Radiant Path',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            NightsOfFormalFocus(),
            DreamOfTheStarStreamShaker(),
        ]


desc: Dict[str, DescDictType] = {
    "CHARACTOR/Layla": {
        "names": {
            "en-US": "Layla",
            "zh-CN": "莱依拉"
        },
        "image_path": "cardface/Char_Avatar_Layla.png",  # noqa: E501
        "id": 1109,
        "descs": {
            "4.3": {
                "en-US": "",
                "zh-CN": ""
            }
        }
    },
    "SKILL_Layla_NORMAL_ATTACK/Sword of the Radiant Path": {
        "names": {
            "en-US": "Sword of the Radiant Path",
            "zh-CN": "熠辉轨度剑"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 2 Physical DMG.",
                "zh-CN": "造成2点物理伤害。"
            }
        }
    },
    "SKILL_Layla_ELEMENTAL_SKILL/Nights of Formal Focus": {
        "names": {
            "en-US": "Nights of Formal Focus",
            "zh-CN": "垂裳端凝之夜"
        },
        "descs": {
            "4.3": {
                "en-US": "Creates Curtain of Slumber Shield and Shooting Star, and collects 1 Night Star for Shooting Star. (If Shooting Star already exists, then collect an extra 2 Night Stars)",  # noqa: E501
                "zh-CN": "生成安眠帷幕护盾和飞星，并为飞星累积1枚「晚星」。（如果飞星已存在，则额外累积2枚「晚星」）"  # noqa: E501
            }
        }
    },
    "TEAM_STATUS/Curtain of Slumber Shield": {
        "names": {
            "en-US": "Curtain of Slumber Shield",
            "zh-CN": "安眠帷幕护盾"
        },
        "descs": {
            "4.3": {
                "en-US": "Provides 2 points of Shield to your active character.",  # noqa: E501
                "zh-CN": "提供2点护盾，保护我方出战角色。"
            }
        }
    },
    "TEAM_STATUS/Shooting Star": {
        "names": {
            "en-US": "Shooting Star",
            "zh-CN": "飞星"
        },
        "descs": {
            "4.3": {
                "en-US": "After one of your characters uses a Skill: Gain 1 Night Star. If possible, consume 4 Night Stars to deal 1 Cryo DMG.",  # noqa: E501
                "zh-CN": "我方角色使用技能后：累积1枚「晚星」。如可能，就消耗4枚「晚星」，造成1点冰元素伤害。"  # noqa: E501
            }
        },
        "image_path": "status/Layla_S.png"
    },
    "SKILL_Layla_ELEMENTAL_BURST/Dream of the Star-Stream Shaker": {
        "names": {
            "en-US": "Dream of the Star-Stream Shaker",
            "zh-CN": "星流摇床之梦"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 3 Cryo DMG, summons 1 Celestial Dreamsphere.",
                "zh-CN": "造成3点冰元素伤害，召唤饰梦天球。"
            }
        }
    },
    "SUMMON/Celestial Dreamsphere": {
        "names": {
            "en-US": "Celestial Dreamsphere",
            "zh-CN": "饰梦天球"
        },
        "descs": {
            "4.3": {
                "en-US": "End Phase: Deal 1 Cryo DMG. If Shooting Star is in play, it will gain 1 Night Star.\nUsage(s): 2",  # noqa: E501
                "zh-CN": "结束阶段：造成1点冰元素伤害。如果飞星在场，则使其累积1枚「晚星」。\n可用次数：2"  # noqa: E501
            }
        }
    },
    "TALENT_Layla/Light's Remit": {
        "names": {
            "en-US": "Light's Remit",
            "zh-CN": "归芒携信"
        },
        "descs": {
            "4.3": {
                "en-US": "Combat Action: When your active character is Layla, equip this card.\nAfter Layla equips this card, immediately use Nights of Formal Focus.\nWhen Layla is on the field and has this card equipped, every time Shooting Star deals DMG, draw 1 card.\n(You must have Layla in your deck to add this card to your deck.)",  # noqa: E501
                "zh-CN": "战斗行动：我方出战角色为莱依拉时，装备此牌。\n莱依拉装备此牌后，立刻使用一次垂裳端凝之夜。\n装备有此牌的莱依拉在场时，每当飞星造成伤害，就抓1张牌。\n（牌组中包含莱依拉，才能加入牌组）"  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Constellation_Layla.png",  # noqa: E501
        "id": 211091
    },
}


register_class(
    Layla_4_3 | CurtainOfSlumberShield_4_3 | ShootingStar_4_3 
    | CelestialDreamsphere_4_3 | LightsRemit_4_3, desc
)
