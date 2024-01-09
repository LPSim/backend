from typing import Any, Dict, List, Literal

from .....utils.class_registry import register_class
from ....status.team_status.base import DefendTeamStatus
from ....summon.base import (
    AttackAndGenerateStatusSummonBase, SwirlChangeSummonBase
)
from ....action import (
    Actions, CreateObjectAction, MakeDamageAction, RemoveObjectAction
)
from ....status.charactor_status.base import RoundEndAttackCharactorStatus
from ....match import Match
from ....event import (
    ReceiveDamageEventArguments, RoundEndEventArguments, 
    RoundPrepareEventArguments
)
from ....struct import Cost
from ....consts import (
    DamageElementalType, DieColor, ElementType, FactionType, IconType, 
    ObjectPositionType, WeaponType
)
from ....charactor.charactor_base import (
    CharactorBase, ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, SkillTalent
)
from .....utils.desc_registry import DescDictType


class OverawingAssault_4_3(RoundEndAttackCharactorStatus):
    name: Literal['Overawing Assault'] = 'Overawing Assault'
    version: Literal['4.3'] = '4.3'
    usage: int = 1
    max_usage: int = 1
    damage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.PIERCING
    icon_type: IconType = IconType.DEBUFF

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction | RemoveObjectAction]:
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        if charactor.hp >= 6:
            # attack self
            return list(super().event_handler_ROUND_END(event, match))
        else:
            # remove self
            self.usage = 0
            return list(self.check_should_remove())


class BogglecatBoxStatus_4_3(DefendTeamStatus):
    name: Literal['Bogglecat Box'] = 'Bogglecat Box'
    version: Literal['4.3'] = '4.3'
    usage: int = 1
    max_usage: int = 1
    min_damage_to_trigger: int = 1
    max_in_one_time: int = 1


class BogglecatBox_4_3(SwirlChangeSummonBase, 
                       AttackAndGenerateStatusSummonBase):
    name: Literal['Bogglecat Box'] = 'Bogglecat Box'
    version: Literal['4.3'] = '4.3'
    usage: int = 2
    max_usage: int = 2
    damage: int = 1

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Match
    ) -> List[Actions]:
        """
        When anyone receives damage, and is pyro/hydro/cryo/electro, and is
        our charactor, and current damage type is anemo, change damage element.
        """
        if self.damage_elemental_type != DamageElementalType.ANEMO:
            # already changed, do nothing
            return []
        if event.final_damage.damage_elemental_type not in [
            DamageElementalType.PYRO, DamageElementalType.HYDRO,
            DamageElementalType.CRYO, DamageElementalType.ELECTRO
        ]:
            # damage element not pyro/hydro/cryo/electro, do nothing
            return []
        if (
            event.final_damage.target_position.player_idx
            != self.position.player_idx
        ):
            # not our player made damage, do nothing
            return []
        # do type change
        self.damage_elemental_type = event.final_damage.damage_elemental_type
        return []


class EnigmaticFeint(ElementalSkillBase):
    name: Literal['Enigmatic Feint'] = 'Enigmatic Feint'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 3
    )
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    use_time_this_round: int = 0

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Match
    ) -> List[Actions]:
        """
        reset use_time_this_round
        """
        self.use_time_this_round = 0
        return []

    def get_actions(self, match: Match) -> List[Actions]:
        self.use_time_this_round += 1
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        talent_equipped = charactor.talent is not None
        if talent_equipped and self.use_time_this_round == 2:
            # second use with talent, deal +2 damage
            self.damage += 2
        ret = super().get_actions(match)
        damage_action = ret[0]
        assert isinstance(damage_action, MakeDamageAction)
        if talent_equipped and self.use_time_this_round == 2:
            # second use with talent, reset damage and force opponent to switch
            self.damage -= 2
            prev_charactor_idx = match.player_tables[
                1 - self.position.player_idx].previous_charactor_idx()
            if prev_charactor_idx is not None:
                damage_action.charactor_change_idx[
                    1 - self.position.player_idx
                ] = prev_charactor_idx
        elif self.use_time_this_round == 1 and charactor.hp <= 8:
            # first use, heal 2 hp and attach status
            heal = self.attack_self(match, -2)
            damage_action.damage_value_list += heal.damage_value_list
            damage_action.create_objects.append(
                CreateObjectAction(
                    object_name = 'Overawing Assault',
                    object_position = charactor.position.set_area(
                        ObjectPositionType.CHARACTOR_STATUS
                    ),
                    object_arguments = {}
                )
            )
        return ret


class MagicTrickAstonishingShift(ElementalBurstBase):
    name: Literal[
        'Magic Trick: Astonishing Shift'] = 'Magic Trick: Astonishing Shift'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 3,
        charge = 2
    )
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.ANEMO

    def get_actions(self, match: Match) -> List[Actions]:
        return super().get_actions(match, [
            self.create_summon('Bogglecat Box', {})
        ])


class AColdBladeLikeAShadow_4_3(SkillTalent):
    name: Literal['A Cold Blade Like a Shadow'] = 'A Cold Blade Like a Shadow'
    version: Literal['4.3'] = '4.3'
    charactor_name: Literal['Lynette'] = 'Lynette'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 3,
    )
    skill: Literal['Enigmatic Feint'] = 'Enigmatic Feint'


class Lynette_4_3(CharactorBase):
    name: Literal['Lynette']
    version: Literal['4.3'] = '4.3'
    element: ElementType = ElementType.ANEMO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | EnigmaticFeint | MagicTrickAstonishingShift
    ] = []
    faction: List[FactionType] = [
        FactionType.FONTAINE, FactionType.FATUI, FactionType.ARKHE_OUSIA
    ]
    weapon_type: WeaponType = WeaponType.SWORD

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = "Rapid Ritesword",
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            EnigmaticFeint(),
            MagicTrickAstonishingShift()
        ]


desc: Dict[str, DescDictType] = {
    "CHARACTOR/Lynette": {
        "names": {
            "en-US": "Lynette",
            "zh-CN": "琳妮特"
        },
        "image_path": "cardface/Char_Avatar_Linette.png",  # noqa E501
        "id": 1508,
        "descs": {
            "4.3": {
                "en-US": "",
                "zh-CN": ""
            }
        }
    },
    "SKILL_Lynette_NORMAL_ATTACK/Rapid Ritesword": {
        "names": {
            "en-US": "Rapid Ritesword",
            "zh-CN": "迅捷礼刺剑"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 2 Physical DMG.",
                "zh-CN": "造成2点物理伤害。"
            }
        }
    },
    "SKILL_Lynette_ELEMENTAL_SKILL/Enigmatic Feint": {
        "names": {
            "en-US": "Enigmatic Feint",
            "zh-CN": "谜影障身法"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 3 Anemo DMG. The first time this Skill is used this Round, heal the user for 2 HP if they have no more than 8 HP, but apply Overawing Assault to the user.",  # noqa: E501
                "zh-CN": "造成3点风元素伤害，本回合第一次使用此技能、且自身生命值不多于8时治疗自身2点，但是附属攻袭余威。"  # noqa: E501
            }
        }
    },
    "CHARACTOR_STATUS/Overawing Assault": {
        "names": {
            "en-US": "Overawing Assault",
            "zh-CN": "攻袭余威"
        },
        "descs": {
            "4.3": {
                "en-US": "End Phase: If this character's HP is at least 6, then they will take 2 Piercing DMG.\nDuration (Rounds): 1",  # noqa: E501
                "zh-CN": "结束阶段：如果角色生命值至少为6，则受到2点穿透伤害。\n持续回合：1"  # noqa: E501
            }
        }
    },
    "SKILL_Lynette_ELEMENTAL_BURST/Magic Trick: Astonishing Shift": {
        "names": {
            "en-US": "Magic Trick: Astonishing Shift",
            "zh-CN": "魔术·运变惊奇"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 2 Anemo DMG, summons 1 Bogglecat Box.",
                "zh-CN": "造成2点风元素伤害，召唤惊奇猫猫盒。"
            }
        }
    },
    "TEAM_STATUS/Bogglecat Box": {
        "names": {
            "en-US": "Bogglecat Box",
            "zh-CN": "惊奇猫猫盒"
        },
        "descs": {
            "4.3": {
                "en-US": "When your active character takes DMG: Decreases DMG taken by 1.",  # noqa: E501
                "zh-CN": "我方出战角色受到伤害时：抵消1点伤害。"
            }
        }
    },
    "SUMMON/Bogglecat Box": {
        "names": {
            "en-US": "Bogglecat Box",
            "zh-CN": "惊奇猫猫盒"
        },
        "descs": {
            "4.3": {
                "en-US": "End Phase: Deals 1 Anemo DMG.\nUsage(s): 2\n\nWhen your active character takes DMG: Decreases DMG taken by 1. (Once per Round)\nWhen your character(s) take Cryo/Hydro/Pyro/Electro DMG: Change the Elemental Type of this card. (Once before leaving play)",  # noqa: E501
                "zh-CN": "结束阶段：造成1点风元素伤害。\n可用次数：2\n\n我方出战角色受到伤害时：抵消1点伤害。（每回合1次）\n我方角色受到冰/水/火/雷伤害时：转换此牌的元素类型。（离场前仅限一次）"  # noqa: E501
            }
        },
        "image_path": "cardface/Summon_Linette.png",  # noqa: E501
    },
    "TALENT_Lynette/A Cold Blade Like a Shadow": {
        "names": {
            "en-US": "A Cold Blade Like a Shadow",
            "zh-CN": "如影流露的冷刃"
        },
        "descs": {
            "4.3": {
                "en-US": "Combat Action: When your active character is Lynette, equip this card.\nAfter Lynette equips this card, immediately use Enigmatic Feint once.\nAfter your Lynette, who has this card equipped, uses Enigmatic Feint for the second time this Round: deals +2 DMG and forces your opponent to switch to their previous character.\n(You must have Lynette in your deck to add this card to your deck.)",  # noqa: E501
                "zh-CN": "战斗行动：我方出战角色为琳妮特时，装备此牌。\n琳妮特装备此牌后，立刻使用一次谜影障身法。\n装备有此牌的琳妮特每回合第二次使用谜影障身法时：伤害+2，并强制敌方切换到前一个角色。\n（牌组中包含琳妮特，才能加入牌组）"  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Constellation_Linette.png",  # noqa: E501
        "id": 215081
    },
}


register_class(
    OverawingAssault_4_3 | BogglecatBoxStatus_4_3 | BogglecatBox_4_3
    | AColdBladeLikeAShadow_4_3 | Lynette_4_3,
    desc
)
