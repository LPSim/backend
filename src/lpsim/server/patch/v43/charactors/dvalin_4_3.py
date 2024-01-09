from typing import Dict, List, Literal

from pydantic import PrivateAttr

from ....action import (
    ActionTypes, Actions, CreateObjectAction, MakeDamageAction, 
    RemoveObjectAction, 
)
from ....event import (
    CreateObjectEventArguments, RemoveObjectEventArguments, 
    RoundPrepareEventArguments
)
from .....utils.class_registry import register_class
from ....status.charactor_status.base import (
    PrepareCharactorStatus, UsageCharactorStatus
)
from ....modifiable_values import DamageIncreaseValue, DamageValue
from ....match import Match
from ....struct import Cost
from ....consts import (
    DamageElementalType, DamageType, DieColor, ElementType, FactionType, 
    IconType, ObjectPositionType, ObjectType, WeaponType
)
from ....charactor.charactor_base import (
    CharactorBase, ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, SkillTalent
)
from .....utils.desc_registry import DescDictType


class TotalCollapse_4_3(UsageCharactorStatus):
    name: Literal['Total Collapse'] = 'Total Collapse'
    version: Literal['4.3'] = '4.3'
    usage: int = 1
    max_usage: int = 1
    icon_type: IconType = IconType.DEBUFF

    available_handler_in_trashbin: List[ActionTypes] = [
        ActionTypes.REMOVE_OBJECT]

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Match,
        mode: Literal['TEST', 'REAL'],
    ) -> DamageIncreaseValue:
        if (
            value.damage_elemental_type != DamageElementalType.PHYSICAL
            and value.damage_elemental_type != DamageElementalType.ANEMO
        ):
            # not right damage type
            return value
        if value.is_corresponding_charactor_receive_damage(
            self.position, match
        ):
            # this charactor receive damage
            assert mode == 'REAL'
            self.usage -= 1
            value.damage += 2
        return value


class PerpetualCleansingStatus_4_3(PrepareCharactorStatus):
    name: Literal['Perpetual Cleansing'] = 'Perpetual Cleansing'
    version: Literal['4.3'] = '4.3'
    charactor_name: Literal['Dvalin'] = 'Dvalin'
    skill_name: Literal['Perpetual Cleansing'] = 'Perpetual Cleansing'


class UltimateCleansingStatus_4_3(PrepareCharactorStatus):
    name: Literal['Ultimate Cleansing'] = 'Ultimate Cleansing'
    version: Literal['4.3'] = '4.3'
    charactor_name: Literal['Dvalin'] = 'Dvalin'
    skill_name: Literal['Ultimate Cleansing'] = 'Ultimate Cleansing'


class TempestuousBarrage(ElementalSkillBase):
    name: Literal['Tempestuous Barrage'] = 'Tempestuous Barrage'
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 3,
    )

    def get_actions(self, match: Match) -> List[Actions]:
        return super().get_actions(match, [
            self.create_opposite_charactor_status(
                match, 'Total Collapse', {}
            )
        ])


class DvalinsCleansing(ElementalSkillBase):
    name: Literal['Dvalin\'s Cleansing'] = 'Dvalin\'s Cleansing'
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 5,
    )

    def get_actions(self, match: Match) -> List[Actions]:
        return super().get_actions(match, [
            self.create_charactor_status('Perpetual Cleansing', {})
        ])


class PerpetualCleansing(ElementalSkillBase):
    name: Literal['Perpetual Cleansing'] = 'Perpetual Cleansing'
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = Cost()

    def is_valid(self, match: Match) -> bool:
        return False

    def get_actions(self, match: Match) -> List[Actions]:
        table = match.player_tables[1 - self.position.player_idx]
        target = table.next_charactor_idx()
        if target is None:
            target = table.active_charactor_idx
        return [
            MakeDamageAction(
                damage_value_list = [
                    DamageValue(
                        position = self.position,
                        damage_type = DamageType.DAMAGE,
                        target_position = table.charactors[target].position,
                        damage = self.damage,
                        damage_elemental_type = self.damage_type,
                        cost = self.cost.copy(),
                    )
                ],
                create_objects = [
                    self.create_charactor_status('Ultimate Cleansing', {})
                ]
            ),
        ]


class UltimateCleansing(ElementalSkillBase):
    name: Literal['Ultimate Cleansing'] = 'Ultimate Cleansing'
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = Cost()

    def is_valid(self, match: Match) -> bool:
        return False

    def get_actions(self, match: Match) -> List[Actions]:
        table = match.player_tables[1 - self.position.player_idx]
        target = table.previous_charactor_idx()
        if target is None:
            target = table.active_charactor_idx
        return [
            MakeDamageAction(
                damage_value_list = [
                    DamageValue(
                        position = self.position,
                        damage_type = DamageType.DAMAGE,
                        target_position = table.charactors[target].position,
                        damage = self.damage,
                        damage_elemental_type = self.damage_type,
                        cost = self.cost.copy(),
                    )
                ]
            ),
        ]


class CaelestinumFinaleTermini(ElementalBurstBase):
    name: Literal['Caelestinum Finale Termini'] = 'Caelestinum Finale Termini'
    damage: int = 5
    damage_type: DamageElementalType = DamageElementalType.ANEMO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 4,
        charge = 2
    )

    def get_actions(self, match: Match) -> List[Actions]:
        ret = super().get_actions(match)
        damage_action = ret[1]
        assert damage_action.type == ActionTypes.MAKE_DAMAGE
        table = match.player_tables[1 - self.position.player_idx]
        for charactor in table.charactors:
            if table.active_charactor_idx == charactor.position.charactor_idx:
                continue
            if charactor.is_defeated:
                continue
            # apply status
            damage_action.create_objects.append(
                CreateObjectAction(
                    object_name = 'Total Collapse',
                    object_position = charactor.position.set_area(
                        ObjectPositionType.CHARACTOR_STATUS),
                    object_arguments = {}
                )
            )
        return ret


class RendingVortex_4_3(SkillTalent):
    name: Literal['Rending Vortex'] = 'Rending Vortex'
    version: Literal['4.3'] = '4.3'
    charactor_name: Literal['Dvalin'] = 'Dvalin'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ANEMO,
        elemental_dice_number = 3
    )
    skill: Literal['Tempestuous Barrage'] = 'Tempestuous Barrage'
    round_usage: int = 1
    _max_round_usage: int = PrivateAttr(1)

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Match
    ) -> List[Actions]:
        self.round_usage = self._max_round_usage
        return []

    def event_handler_CREATE_OBJECT(
        self, event: CreateObjectEventArguments, match: Match
    ) -> List[CreateObjectAction]:
        """
        when Total collapse is renew create, treat it as old one removed.
        """
        if event.create_result != 'RENEW':
            # not renew, do nothing
            return []
        # make fake event arguments
        fake_event = RemoveObjectEventArguments(
            action = RemoveObjectAction(
                object_position = event.action.object_position,
            ),
            object_name = event.action.object_name,
            # no effect, set one default
            object_type = ObjectType.CHARACTOR_STATUS,
        )
        ret = self.event_handler_REMOVE_OBJECT(fake_event, match)
        return ret

    def event_handler_REMOVE_OBJECT(
        self, event: RemoveObjectEventArguments, match: Match
    ) -> List[CreateObjectAction]:
        """
        When opposite Total Collapse removed, and opposite is active, and found 
        self is in charactor, create Total Collapse on next standby charactor.
        """
        if self.round_usage <= 0:
            # no usage
            return []
        if event.object_name != 'Total Collapse':
            # not Total Collapse
            return []
        if not self.position.check_position_valid(
            event.action.object_position, match, player_idx_same = False,
            source_area = ObjectPositionType.CHARACTOR,
            target_is_active_charactor = True, 
        ):
            # not from opposite active charactor, or self not equipped
            return []
        # is opposite active, append Total Collapse to next standby charactor
        table = match.player_tables[1 - self.position.player_idx]
        target = table.next_charactor_idx()
        if target is None:
            # no target, do nothing
            return []
        self.round_usage -= 1
        target_charactor = table.charactors[target]
        return [
            CreateObjectAction(
                object_name = 'Total Collapse',
                object_position 
                = target_charactor.position.set_area(
                    ObjectPositionType.CHARACTOR_STATUS),
                object_arguments = {}
            )
        ]


class Dvalin_4_3(CharactorBase):
    name: Literal['Dvalin']
    version: Literal['4.3'] = '4.3'
    element: ElementType = ElementType.ANEMO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | TempestuousBarrage | DvalinsCleansing 
        | PerpetualCleansing | UltimateCleansing | CaelestinumFinaleTermini
    ] = []
    faction: List[FactionType] = [
        FactionType.MONSTER
    ]
    weapon_type: WeaponType = WeaponType.OTHER

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Lacerating Slash',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            TempestuousBarrage(),
            DvalinsCleansing(),
            PerpetualCleansing(),
            UltimateCleansing(),
            CaelestinumFinaleTermini(),
        ]


desc: Dict[str, DescDictType] = {
    "CHARACTOR/Dvalin": {
        "names": {
            "en-US": "Dvalin",
            "zh-CN": "特瓦林"
        },
        "image_path": "cardface/Char_Monster_Dvalin.png",  # noqa: E501
        "id": 2502,
        "descs": {
            "4.3": {
                "en-US": "",
                "zh-CN": ""
            }
        }
    },
    "SKILL_Dvalin_NORMAL_ATTACK/Lacerating Slash": {
        "names": {
            "en-US": "Lacerating Slash",
            "zh-CN": "裂爪横击"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 2 Physical DMG.",
                "zh-CN": "造成2点物理伤害。"
            }
        }
    },
    "SKILL_Dvalin_ELEMENTAL_SKILL/Tempestuous Barrage": {
        "names": {
            "en-US": "Tempestuous Barrage",
            "zh-CN": "暴风轰击"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 2 Anemo DMG. The target character receives Total Collapse.",  # noqa: E501
                "zh-CN": "造成2点风元素伤害，目标角色附属坍毁。"
            }
        }
    },
    "CHARACTOR_STATUS/Total Collapse": {
        "names": {
            "en-US": "Total Collapse",
            "zh-CN": "坍毁"
        },
        "descs": {
            "4.3": {
                "en-US": "Physical DMG or Anemo DMG taken by the affected character increased by 2.\nUsage(s): 1",  # noqa: E501
                "zh-CN": "所附属角色受到的物理伤害或风元素伤害+2。\n可用次数：1"
            }
        }
    },
    "SKILL_Dvalin_ELEMENTAL_SKILL/Dvalin's Cleansing": {
        "names": {
            "en-US": "Dvalin's Cleansing",
            "zh-CN": "风龙涤流"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 2 Anemo DMG and then separately performs \"Prepare Skill|s1:prepares\" for Perpetual Cleansing and Ultimate Cleansing.",  # noqa: E501
                "zh-CN": "造成2点风元素伤害，然后分别准备技能：长延涤流和终幕涤流。"
            }
        }
    },
    "CHARACTOR_STATUS/Perpetual Cleansing": {
        "names": {
            "en-US": "Perpetual Cleansing",
            "zh-CN": "长延涤流"
        },
        "descs": {
            "4.3": {
                "en-US": "Elemental Skill\n(Prepare for 1 turn)\nDeals 1 Anemo DMG the next opposing character on standby. After this, Prepare Skill|s1:prepares: Ultimate Cleansing. (If there are no opposing characters on standby, deals DMG to active character instead)",  # noqa: E501
                "zh-CN": "元素战技\n（需准备1个行动轮）\n对下一个敌方后台角色造成1点风元素伤害，然后准备技能：终幕涤流。（敌方没有后台角色时，改为对出战角色造成伤害）"  # noqa: E501
            }
        }
    },
    "CHARACTOR_STATUS/Ultimate Cleansing": {
        "names": {
            "en-US": "Ultimate Cleansing",
            "zh-CN": "终幕涤流"
        },
        "descs": {
            "4.3": {
                "en-US": "Elemental Skill\n(Prepare for 1 turn)\nDeals 2 Anemo DMG the previous opposing character on standby. (If there are no opposing characters on standby, deals DMG to the active character instead)",  # noqa: E501
                "zh-CN": "元素战技\n（需准备1个行动轮）\n对上一个敌方后台角色造成2点风元素伤害。（敌方没有后台角色时，改为对出战角色造成伤害）"  # noqa: E501
            }
        }
    },
    "SKILL_Dvalin_ELEMENTAL_BURST/Caelestinum Finale Termini": {
        "names": {
            "en-US": "Caelestinum Finale Termini",
            "zh-CN": "终天闭幕曲"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 5 Anemo DMG. Applies Total Collapse to all opposing standby characters.",  # noqa: E501
                "zh-CN": "造成5点风元素伤害，所有敌方后台角色附属坍毁。"
            }
        }
    },
    "SKILL_Dvalin_ELEMENTAL_SKILL/Perpetual Cleansing": {
        "names": {
            "en-US": "Perpetual Cleansing",
            "zh-CN": "长延涤流"
        },
        "descs": {
            "4.3": {
                "en-US": "(Prepare for 1 turn)\nDeals 1 Anemo DMG the next opposing character on standby. After this, Prepare Skill|s1:prepares: Ultimate Cleansing. (If there are no opposing characters on standby, deals DMG to active character instead)",  # noqa: E501
                "zh-CN": "（需准备1个行动轮）\n对下一个敌方后台角色造成1点风元素伤害，然后准备技能：终幕涤流。（敌方没有后台角色时，改为对出战角色造成伤害）"  # noqa: E501
            }
        }
    },
    "SKILL_Dvalin_ELEMENTAL_SKILL/Ultimate Cleansing": {
        "names": {
            "en-US": "Ultimate Cleansing",
            "zh-CN": "终幕涤流"
        },
        "descs": {
            "4.3": {
                "en-US": "(Prepare for 1 turn)\nDeals 2 Anemo DMG the previous opposing character on standby. (If there are no opposing characters on standby, deals DMG to the active character instead)",  # noqa: E501
                "zh-CN": "（需准备1个行动轮）\n对上一个敌方后台角色造成2点风元素伤害。（敌方没有后台角色时，改为对出战角色造成伤害）"  # noqa: E501
            }
        }
    },
    "TALENT_Dvalin/Rending Vortex": {
        "names": {
            "en-US": "Rending Vortex",
            "zh-CN": "毁裂风涡"
        },
        "descs": {
            "4.3": {
                "en-US": "Combat Action: When your active character is Dvalin, equip this card.\nAfter Dvalin equips this card, immediately use Tempestuous Barrage once.\nWhen your Dvalin, who has this card equipped, is on the field, when Total Collapse attached to opposing active character is removed: Apply Total Collapse to the next opposing standby character. (Once per Round)\n(You must have Dvalinin your deck to add this card to your deck.)",  # noqa: E501
                "zh-CN": "战斗行动：我方出战角色为特瓦林时，装备此牌。\n特瓦林装备此牌后，立刻使用一次暴风轰击。\n装备有此牌的特瓦林在场时，敌方出战角色所附属的坍毁状态被移除后：对下一个敌方后台角色附属坍毁。（每回合1次）\n（牌组中包含特瓦林，才能加入牌组）"  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Talent_Dvalin.png",  # noqa: E501
        "id": 225021
    },
}


register_class(
    TotalCollapse_4_3 | PerpetualCleansingStatus_4_3 
    | UltimateCleansingStatus_4_3 | RendingVortex_4_3 | Dvalin_4_3, desc
)
