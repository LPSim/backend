from typing import Any, Dict, List, Literal

from ....status.charactor_status.base import CharactorStatusBase
from ....action import (
    Actions, ChangeObjectUsageAction, CreateObjectAction, DrawCardAction, 
    MakeDamageAction, RemoveObjectAction
)
from .....utils.class_registry import register_class
from ....summon.base import AttackerSummonBase
from ....status.team_status.base import TeamStatusBase
from ....event import (
    GameStartEventArguments, ReceiveDamageEventArguments, 
    RoundEndEventArguments, RoundPrepareEventArguments, SkillEndEventArguments
)
from ....player_table import PlayerTable
from ....modifiable_values import DamageIncreaseValue, DamageValue
from ....match import Match
from ....struct import Cost, ObjectPosition
from ....charactor.charactor_base import (
    CharactorBase, ElementalBurstBase, ElementalNormalAttackBase, 
    ElementalSkillBase, PassiveSkillBase, TalentBase
)
from ....consts import (
    ELEMENT_TO_DAMAGE_TYPE, CostLabels, DamageElementalType, DamageType, 
    DieColor, ElementType, FactionType, IconType, ObjectPositionType, 
    ObjectType, WeaponType
)
from .....utils.desc_registry import DescDictType


class LightningStrikeProbe_4_3(TeamStatusBase):
    name: Literal["Lightning Strike Probe"] = "Lightning Strike Probe"
    version: Literal['4.3'] = '4.3'
    usage: int = 1
    max_usage: int = 1
    icon_type: IconType = IconType.OTHERS

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Match
    ) -> List[Actions]:
        """
        When round prepare, reset usage
        """
        self.usage = self.max_usage
        return []

    def event_handler_SKILL_END(
        self, skill: SkillEndEventArguments, match: Match
    ) -> List[CreateObjectAction | RemoveObjectAction]:
        """
        When skill end, if skill user is on this side, attach lightning rod to
        active charactor.
        """
        if self.usage == 0:
            # no usage left, do nothing
            return []
        if skill.action.position.player_idx != self.position.player_idx:
            # not on this side, do nothing
            return []
        ret: List[CreateObjectAction | RemoveObjectAction] = []
        # check if any charactor has lightning rod attached
        charactors = match.player_tables[self.position.player_idx].charactors
        for charactor in charactors:
            for status in charactor.status:
                if status.name == 'Lightning Rod':
                    # lightning rod already attached, remove
                    ret.append(RemoveObjectAction(
                        object_position = status.position
                    ))
        # attach lightning rod to the charactor
        self.usage -= 1
        ret.append(CreateObjectAction(
            object_name = 'Lightning Rod',
            object_position = skill.action.position.set_area(
                ObjectPositionType.CHARACTOR_STATUS
            ),
            object_arguments = {}
        ))
        return ret


class LightningRod_4_3(CharactorStatusBase):
    name: Literal["Lightning Rod"] = "Lightning Rod"
    version: Literal['4.3'] = '4.3'
    usage: int = 1
    max_usage: int = 1
    icon_type: IconType = IconType.DEBUFF

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Match, 
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        """
        Opponent charactor with lightning rod attached take damage, increase
        damage by 1.
        """
        if self.usage == 0:
            # no usage left, do nothing
            return value
        if not value.is_corresponding_charactor_receive_damage(
            self.position, match, ignore_piercing = False
        ):
            # not corresponding charactor, do nothing
            return value
        if value.position.player_idx == self.position.player_idx:
            # damage from self, do nothing
            return value
        source = match.get_object(value.position)
        if source is not None and source.type == ObjectType.SKILL:
            # is skill, find corresponding charactor
            source = match.player_tables[value.position.player_idx].charactors[
                value.position.charactor_idx]
        if (
            source is None or source.name not in [
                'Thunder Manifestation', 'Thundering Shackles'
            ]
        ):
            # not from thunder manifestation or its summon, do nothing
            return value
        # increase damage by 1
        value.damage += 1
        assert mode == 'REAL'
        self.usage -= 1
        return value


def get_lightning_rod_target_idx(table: PlayerTable) -> int:
    """
    find charactor idx from table that has lightning rod attached. If no such
    charactor, return active charactor idx.
    """
    target: int | None = None
    for cid, charactor in enumerate(table.charactors):
        for status in charactor.status:
            if status.name == 'Lightning Rod':
                target = cid
                break
        if target is not None:
            break
    if target is None:
        target = table.active_charactor_idx
    return target


class ThunderingShacklesSummon_4_3(AttackerSummonBase):
    name: Literal["Thundering Shackles"] = "Thundering Shackles"
    version: Literal['4.3'] = '4.3'
    usage: int = 1
    max_usage: int = 1
    damage: int = 3
    damage_elemental_type: DamageElementalType = DamageElementalType.ELECTRO

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction | ChangeObjectUsageAction]:
        """
        When round end, make damage to right target, and decrease self usage.
        """
        assert self.usage > 0
        damage_type = DamageType.DAMAGE
        table = match.player_tables[1 - self.position.player_idx]
        target = get_lightning_rod_target_idx(table)
        return [
            MakeDamageAction(
                damage_value_list = [
                    DamageValue(
                        position = self.position,
                        damage_type = damage_type,
                        target_position = table.charactors[target].position,
                        damage = self.damage,
                        damage_elemental_type = self.damage_elemental_type,
                        cost = Cost(),
                    )
                ],
            ),
            ChangeObjectUsageAction(
                object_position = self.position,
                change_usage = -1
            )
        ]


class StrifefulLightning(ElementalSkillBase):
    name: Literal["Strifeful Lightning"] = "Strifeful Lightning"
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3,
    )

    def get_actions(self, match: Match) -> List[Actions]:
        """
        Attack target with Lightning Rod attached.
        """
        table = match.player_tables[1 - self.position.player_idx]
        target = get_lightning_rod_target_idx(table)
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
            ),
            self.charge_self(1)
        ]


class ThunderingShackles(ElementalBurstBase):
    name: Literal["Thundering Shackles"] = "Thundering Shackles"
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3,
        charge = 2,
    )

    def get_actions(self, match: Match) -> List[Actions]:
        return super().get_actions(match, [
            self.create_summon('Thundering Shackles'),
        ])


class LightningProbe(PassiveSkillBase):
    name: Literal["Lightning Probe"] = "Lightning Probe"

    def event_handler_GAME_START(
        self, event: GameStartEventArguments, match: Match
    ) -> List[CreateObjectAction]:
        """
        When game start, create Lightning Strike Probe on opponent's side.
        """
        return [
            CreateObjectAction(
                object_name = 'Lightning Strike Probe',
                object_position = ObjectPosition(
                    player_idx = 1 - self.position.player_idx,
                    area = ObjectPositionType.TEAM_STATUS,
                    id = -1,
                ),
                object_arguments = {}
            )
        ]


class GrievingEcho_4_3(TalentBase):
    name: Literal["Grieving Echo"] = "Grieving Echo"
    version: Literal['4.3'] = '4.3'
    charactor_name: Literal["Thunder Manifestation"] = "Thunder Manifestation"
    cost_label: int = (
        CostLabels.CARD.value | CostLabels.TALENT.value 
        | CostLabels.EQUIPMENT.value
    )
    cost: Cost = Cost()
    usage: int = 1

    def is_valid(self, match: Any) -> bool:
        if self.position.area != ObjectPositionType.HAND:
            # not in hand, cannot equip
            raise AssertionError('Talent is not in hand')
        return len(self.get_targets(match)) > 0

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        """
        All ayaka are targets
        """
        assert self.position.area != ObjectPositionType.CHARACTOR
        ret: List[ObjectPosition] = []
        for c in match.player_tables[self.position.player_idx].charactors:
            if c.name == self.charactor_name and c.is_alive:
                ret.append(c.position)
        return ret

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Match
    ) -> List[Actions]:
        """
        When round prepare, reset usage
        """
        self.usage = 1
        return []

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Match
    ) -> List[DrawCardAction]:
        """
        Opponent charactor with lightning rod attached take damage, draw card.
        """
        target_position = event.final_damage.target_position
        if self.position.area != ObjectPositionType.CHARACTOR:
            # not equipped, do nothing
            return []
        if self.usage <= 0:
            # no usage left, do nothing
            return []
        if target_position.player_idx == self.position.player_idx:
            # damage to self, do nothing
            return []
        target_charactor: CharactorBase = match.get_object(
            target_position)  # type: ignore
        for status in target_charactor.status:
            if status.name == 'Lightning Rod':
                # opposite charactor has lightning rod attached, draw card
                self.usage = 0
                return [
                    DrawCardAction(
                        player_idx = self.position.player_idx,
                        number = 1,
                        draw_if_filtered_not_enough = True
                    )
                ]
        return []


class ThunderManifestation_4_3(CharactorBase):
    name: Literal["Thunder Manifestation"]
    version: Literal['4.3'] = '4.3'
    element: ElementType = ElementType.ELECTRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        ElementalNormalAttackBase | StrifefulLightning | ThunderingShackles
        | LightningProbe
    ] = []
    faction: List[FactionType] = [
        FactionType.MONSTER
    ]
    weapon_type: WeaponType = WeaponType.OTHER

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name = 'Thunderous Wingslash',
                damage_type = ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost = ElementalNormalAttackBase.get_cost(self.element),
            ),
            StrifefulLightning(),
            ThunderingShackles(),
            LightningProbe(),
        ]


desc: Dict[str, DescDictType] = {
    "CHARACTOR/Thunder Manifestation": {
        "names": {
            "en-US": "Thunder Manifestation",
            "zh-CN": "雷音权现"
        },
        "image_path": "cardface/Char_Monster_Raijin.png",  # noqa: E501
        "id": 2402,
        "descs": {
            "4.3": {
                "en-US": "",
                "zh-CN": ""
            }
        }
    },
    "SKILL_Thunder Manifestation_NORMAL_ATTACK/Thunderous Wingslash": {
        "names": {
            "en-US": "Thunderous Wingslash",
            "zh-CN": "轰霆翼斩"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 1 Electro DMG.",
                "zh-CN": "造成1点雷元素伤害。"
            }
        }
    },
    "SKILL_Thunder Manifestation_ELEMENTAL_SKILL/Strifeful Lightning": {
        "names": {
            "en-US": "Strifeful Lightning",
            "zh-CN": "雷墙倾轧"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 3 Electro DMG to opposing characters affected by Lightning Rod. (If there are no eligible opposing characters, deals DMG to the active character instead)",  # noqa: E501
                "zh-CN": "对附属有雷鸣探知的敌方角色造成3点雷元素伤害。（如果敌方不存在符合条件角色，则改为对出战角色造成伤害）"  # noqa: E501
            }
        }
    },
    "CHARACTOR_STATUS/Lightning Rod": {
        "names": {
            "en-US": "Lightning Rod",
            "zh-CN": "雷鸣探知"
        },
        "descs": {
            "4.3": {
                "en-US": "While this status is active, can be triggered once: DMG received by the attached character from Thunder Manifestation or its summons is increased by 1.\n(Only one of this status can exist on the field at once. Some of Thunder Manifestation's skills will target the character to which this is attached.)",  # noqa: E501
                "zh-CN": "此状态存在期间，可以触发1次：所附属角色受到雷音权现及其召唤物造成的伤害+1。\n（同一方场上最多存在一个此状态。雷音权现的部分技能，会以所附属角色为目标。）"  # noqa: E501
            }
        }
    },
    "SKILL_Thunder Manifestation_ELEMENTAL_BURST/Thundering Shackles": {
        "names": {
            "en-US": "Thundering Shackles",
            "zh-CN": "轰雷禁锢"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 2 Electro DMG, summons 1 Thundering Shackles.",
                "zh-CN": "造成2点雷元素伤害，召唤轰雷禁锢。"
            }
        }
    },
    "SUMMON/Thundering Shackles": {
        "names": {
            "en-US": "Thundering Shackles",
            "zh-CN": "轰雷禁锢"
        },
        "descs": {
            "4.3": {
                "en-US": "End Phase: Deals 3 Electro DMG to opposing characters affected by Lightning Rod. (If there are no eligible opposing characters, deals DMG to the active character instead)\nUsage(s): 1",  # noqa: E501
                "zh-CN": "结束阶段：对附属有雷鸣探知的敌方角色造成造成3点雷元素伤害。（如果敌方不存在符合条件角色，则改为对出战角色造成伤害）\n可用次数：1"  # noqa: E501
            }
        }
    },
    "SKILL_Thunder Manifestation_PASSIVE/Lightning Probe": {
        "names": {
            "en-US": "Lightning Probe",
            "zh-CN": "雷霆探知"
        },
        "descs": {
            "4.3": {
                "en-US": "(Passive) When battle begins, create a Lightning Strike Probe on the opponent's side of the field.",  # noqa: E501
                "zh-CN": "【被动】战斗开始时，在敌方场上生成雷霆探针。"
            }
        }
    },
    "TEAM_STATUS/Lightning Strike Probe": {
        "names": {
            "en-US": "Lightning Strike Probe",
            "zh-CN": "雷霆探针"
        },
        "descs": {
            "4.3": {
                "en-US": "After a character on whose side of the field this card is on uses a Skill: Attach Lightning Rod to the active character on that side. (Once per Round)",  # noqa: E501
                "zh-CN": "所在阵营角色使用技能后：对所在阵营出战角色附属雷鸣探知。（每回合1次）"
            }
        },
        "image_path": "status/Debuff_Raijin_S.png"
    },
    "TALENT_Thunder Manifestation/Grieving Echo": {
        "names": {
            "en-US": "Grieving Echo",
            "zh-CN": "悲号回唱"
        },
        "descs": {
            "4.3": {
                "en-US": "When Thunder Manifestation, with this card equipped, is in play, when opponents with Lightning Rod attached take DMG: You draw 1 card (Once per Round)\n(Your deck must contain Thunder Manifestation to add this card to your deck)",  # noqa: E501
                "zh-CN": "装备有此牌的雷音权现在场，附属有雷鸣探知的敌方角色受到伤害时：我方抓1张牌。（每回合1次）\n（牌组中包含雷音权现，才能加入牌组）"  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Talent_Raijin.png",  # noqa: E501
        "id": 224021
    },
}


register_class(
    LightningRod_4_3 | LightningStrikeProbe_4_3 | ThunderingShacklesSummon_4_3
    | GrievingEcho_4_3 | ThunderManifestation_4_3, desc
)
