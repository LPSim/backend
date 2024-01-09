from typing import Dict, List, Literal, Set, Tuple

from .....utils.class_registry import register_class
from ....modifiable_values import DamageIncreaseValue
from ....status.charactor_status.base import CharactorStatusBase
from ....action import (
    Actions, CreateDiceAction, CreateObjectAction, RemoveObjectAction
)
from ....event import (
    AfterMakeDamageEventArguments, ReceiveDamageEventArguments
)
from ....match import Match
from ....struct import Cost, ObjectPosition
from ....charactor.charactor_base import (
    CharactorBase, CreateStatusPassiveSkill, ElementalBurstBase, 
    ElementalSkillBase, PhysicalNormalAttackBase, TalentBase, 
)
from ....consts import (
    DAMAGE_TYPE_TO_ELEMENT, ELEMENT_TO_DAMAGE_TYPE, ELEMENT_TO_DIE_COLOR, 
    CostLabels, DamageElementalType, DamageType, DieColor, ElementType, 
    ElementalReactionType, FactionType, IconType, ObjectPositionType, 
    PlayerActionLabels, SkillType, WeaponType
)
from .....utils.desc_registry import DescDictType


class StoneFacetsElementalCrystallization_4_3(CharactorStatusBase):
    """
    No actions will be taken by this status; all related actions are handled
    in Stone Facets: Elemental Absorption.
    """
    name: Literal[
        'Stone Facets: Elemental Crystallization',
    ] = 'Stone Facets: Elemental Crystallization'
    version: Literal['4.3'] = '4.3'
    usage: int = 0
    max_usage: int = 0
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS


class StoneFacetsElementalAbsorption_4_3(CharactorStatusBase):
    """
    It will handle all side effects of Azhdaha's skills, which includes:
    1. When Azhdaha makes elemental skill damage and triggers crystallize,
        it will absorb the element.
    2. When Azhdaha makes elemental skill damage but not trigger crystallize,
        it will generate charactor status Stone Facets: Elemental 
        Crystallization.
    3. When Azhdaha takes elemental damage, and has charactor status Stone
        Facets: Elemental Crystallization, it will absorb the element.
    4. When Azhdaha absorbs an element, it will override current element
        recorded in the status, and generate elemental die if needed.
    5. When Azhdaha uses elemental burst, based on the number of elements
        absorbed, it will increase damage.
    """
    name: Literal[
        'Stone Facets: Elemental Absorption',
    ] = 'Stone Facets: Elemental Absorption'
    version: Literal['4.3'] = '4.3'
    usage: int = 0
    max_usage: int = 0
    icon_type: Literal[IconType.BUFF] = IconType.BUFF

    current_damage_element: DamageElementalType = DamageElementalType.GEO
    absorbed_elements: List[DamageElementalType] = []

    def absorb_element(self, element: ElementType) -> List[CreateDiceAction]:
        """
        Handle 4.
        """
        dmg_element = ELEMENT_TO_DAMAGE_TYPE[element]
        res: List[CreateDiceAction] = []
        if dmg_element != self.current_damage_element:
            # generate die
            res.append(CreateDiceAction(
                player_idx = self.position.player_idx,
                number = 1,
                color = ELEMENT_TO_DIE_COLOR[element],
            ))
        self.current_damage_element = dmg_element
        if dmg_element not in self.absorbed_elements:
            self.absorbed_elements.append(dmg_element)
            self.usage = len(self.absorbed_elements)
        return res

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Match
    ) -> List[Actions]:
        """
        Handle 1, 2 and 3.
        """
        dmg = event.final_damage
        if (
            self.position.check_position_valid(
                dmg.position, match, player_idx_same = True, 
                charactor_idx_same = True, 
                target_area = ObjectPositionType.SKILL,
            )
            and not dmg.damage_from_element_reaction
        ):
            # is self use skill damage, check for 1 and 2
            skill = match.get_object(dmg.position)
            assert skill is not None
            if skill.name == 'Aura of Majesty':
                # is geo elemental skill
                if dmg.element_reaction == ElementalReactionType.CRYSTALLIZE:
                    # trigger crystallize, 1
                    target_element = dmg.reacted_elements[1]
                    assert target_element != ElementType.GEO
                    return list(self.absorb_element(target_element))
                else:
                    # not trigger crystallize, 2
                    return [
                        CreateObjectAction(
                            object_name = (
                                'Stone Facets: Elemental Crystallization'
                            ),
                            object_position = self.position,
                            object_arguments = {}
                        )
                    ]
        elif self.position.check_position_valid(
            dmg.target_position, match, player_idx_same = True,
            charactor_idx_same = True,
        ):
            # is self take damage, check for 3
            if (
                dmg.damage_type != DamageType.DAMAGE
                or dmg.damage_elemental_type not in [
                    DamageElementalType.CRYO,
                    DamageElementalType.HYDRO,
                    DamageElementalType.PYRO,
                    DamageElementalType.ELECTRO,
                ]
                or dmg.damage_elemental_type == self.current_damage_element
            ):
                # not damage, or elemental type not right, or currently 
                # abosrbed this element, do nothing
                return []
            crystallization_status = None
            for s in match.player_tables[
                self.position.player_idx
            ].charactors[self.position.charactor_idx].status:
                if s.name == 'Stone Facets: Elemental Crystallization':
                    crystallization_status = s
                    break
            if crystallization_status is None:
                # not have crystallization status, do nothing
                return []
            # absorb element, and remove crystallization status
            return list(self.absorb_element(
                DAMAGE_TYPE_TO_ELEMENT[dmg.damage_elemental_type]
            ) + [
                RemoveObjectAction(
                    object_position = crystallization_status.position
                )
            ])
        return []

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Match, 
        mode: Literal['REAL', 'TEST']
    ) -> DamageIncreaseValue:
        """
        Handle 5.
        """
        if (
            not value.is_corresponding_charactor_use_damage_skill(
                self.position, match, SkillType.ELEMENTAL_BURST
            )
            or value.damage_from_element_reaction
        ):
            # not corresponding charactor use elemental burst, 
            # or from elemental reaction, do nothing
            return value
        assert mode == 'REAL'
        # increase damage
        value.damage += len(self.absorbed_elements)
        return value


class AuraOfMajesty(ElementalSkillBase):
    """
    In this skill, only make damage. All side effects will be handled in
    Stone Facets: Elemental Absorption.
    """
    name: Literal['Aura of Majesty'] = 'Aura of Majesty'
    damage_type: DamageElementalType = DamageElementalType.GEO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.GEO,
        elemental_dice_number = 3,
    )


class AzhdahaOtherElementalSkill(ElementalSkillBase):
    """
    For Azhdaha, it can use other elemental skills when absorbed an element.
    This class do normal damage, except that will check whether Azhdaha has
    absorbed an element, so that can use it.
    """
    name: Literal[
        'Frostspike Wave',
        'Torrential Rebuke',
        'Blazing Rebuke',
        'Thunderstorm Wave',
    ]
    # these two attributes will be override in __init__
    damage_type: DamageElementalType = DamageElementalType.PIERCING
    cost: Cost = Cost()

    def __init__(self, *argv, **kwargs) -> None:
        super().__init__(*argv, **kwargs)
        if self.name == 'Frostspike Wave':
            self.damage_type = DamageElementalType.CRYO
        elif self.name == 'Torrential Rebuke':
            self.damage_type = DamageElementalType.HYDRO
        elif self.name == 'Blazing Rebuke':
            self.damage_type = DamageElementalType.PYRO
        elif self.name == 'Thunderstorm Wave':
            self.damage_type = DamageElementalType.ELECTRO
        else:
            raise AssertionError('Unknown skill name')
        self.cost = Cost(
            elemental_dice_color = ELEMENT_TO_DIE_COLOR[
                DAMAGE_TYPE_TO_ELEMENT[self.damage_type]
            ],
            elemental_dice_number = 3,
        )

    def is_valid(self, match: Match) -> bool:
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        status = charactor.status
        for s in status:
            if s.name == 'Stone Facets: Elemental Absorption':  # pragma: no branch  # noqa: E501
                # find the status, check whether it has absorbed right element
                return (
                    s.current_damage_element  # type: ignore
                    == self.damage_type
                )
        raise AssertionError(
            'Stone Facets: Elemental Absorption not found')

    def get_actions(
        self, match: Match
    ) -> List[Actions]:
        return super().get_actions(match, [self.create_charactor_status(
            'Stone Facets: Elemental Crystallization')
        ])


class DecimatingRockfall(ElementalBurstBase):
    """
    Its damage increase is handled in Stone Facets: Elemental Absorption.
    """
    name: Literal['Decimating Rockfall'] = 'Decimating Rockfall'
    damage: int = 4
    damage_type: DamageElementalType = DamageElementalType.GEO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.GEO,
        elemental_dice_number = 3,
        charge = 2
    )


class StoneFacets(CreateStatusPassiveSkill):
    name: Literal['Stone Facets'] = 'Stone Facets'
    status_name: Literal[
        'Stone Facets: Elemental Absorption'
    ] = 'Stone Facets: Elemental Absorption'


class LunarCyclesUnending_4_3(TalentBase):
    name: Literal['Lunar Cycles Unending']
    version: Literal['4.3'] = '4.3'
    charactor_name: Literal['Azhdaha'] = 'Azhdaha'
    cost: Cost = Cost(same_dice_number = 2)
    cost_label: int = (
        CostLabels.CARD.value | CostLabels.TALENT.value
        | CostLabels.EVENT.value
    )
    remove_when_used: bool = True

    def get_action_type(self, match: Match) -> Tuple[int, bool]:
        return PlayerActionLabels.CARD.value, True

    def get_actions(
        self, target: ObjectPosition | None, match: Match
    ) -> List[CreateDiceAction | CreateObjectAction]:
        """
        Create status, and create dice.
        """
        charactors = match.player_tables[self.position.player_idx].charactors
        charactor = match.player_tables[
            self.position.player_idx].get_active_charactor()
        assert charactor.name == self.charactor_name
        elements: Set[ElementType] = set()
        for c in charactors:
            elements.add(c.element)
        ret: List[CreateDiceAction | CreateObjectAction] = [
            CreateObjectAction(
                object_name = 'Stone Facets: Elemental Crystallization',
                object_position = charactor.position.set_area(
                    ObjectPositionType.CHARACTOR_STATUS),
                object_arguments = {}
            )
        ]
        for e in elements:
            ret.append(CreateDiceAction(
                player_idx = self.position.player_idx,
                number = 1,
                color = ELEMENT_TO_DIE_COLOR[e],
            ))
        return ret


class Azhdaha_4_3(CharactorBase):
    name: Literal['Azhdaha']
    desc: Literal['', 'CRYO', 'ELECTRO', 'PYRO', 'HYDRO'] = ''
    version: Literal['4.3'] = '4.3'
    element: ElementType = ElementType.GEO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | AuraOfMajesty | AzhdahaOtherElementalSkill
        | DecimatingRockfall | StoneFacets
    ] = []
    faction: List[FactionType] = [
        FactionType.MONSTER
    ]
    weapon_type: WeaponType = WeaponType.OTHER

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Sundering Charge',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            AuraOfMajesty(),
            AzhdahaOtherElementalSkill(name = 'Frostspike Wave'),
            AzhdahaOtherElementalSkill(name = 'Torrential Rebuke'),
            AzhdahaOtherElementalSkill(name = 'Blazing Rebuke'),
            AzhdahaOtherElementalSkill(name = 'Thunderstorm Wave'),
            DecimatingRockfall(),
            StoneFacets(),
        ]

    def event_handler_AFTER_MAKE_DAMAGE(
        self, event: AfterMakeDamageEventArguments, match: Match
    ) -> List[Actions]:
        """
        After make damage, based on element absorbed, change self desc.
        """
        if self.is_defeated:  # pragma: no cover
            return []
        status = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx].status
        target: StoneFacetsElementalAbsorption_4_3 | None = None
        for s in status:  # pragma: no branch
            if s.name == 'Stone Facets: Elemental Absorption':  # pragma: no branch  # noqa: E501
                target = s  # type: ignore
                break
        assert target is not None
        element = target.current_damage_element
        if element == DamageElementalType.GEO:
            self.desc = ''
        elif element == DamageElementalType.CRYO:
            self.desc = 'CRYO'
        elif element == DamageElementalType.ELECTRO:
            self.desc = 'ELECTRO'
        elif element == DamageElementalType.PYRO:
            self.desc = 'PYRO'
        elif element == DamageElementalType.HYDRO:
            self.desc = 'HYDRO'
        else:
            raise AssertionError(f'Unknown element {element.name}')
        return []


desc: Dict[str, DescDictType] = {
    "CHARACTOR/Azhdaha": {
        "names": {
            "en-US": "Azhdaha",
            "zh-CN": "若陀龙王"
        },
        "descs": {
            "4.3": {
                "en-US": "",
                "zh-CN": ""
            }
        },
        "image_path": "cardface/Char_Monster_Dahaka.png",  # noqa: E501
        "id": 2602
    },
    "CHARACTOR/Azhdaha_CRYO": {
        "names": {
            "en-US": "Azhdaha·Cryo",
            "zh-CN": "若陀龙王·冰"
        },
        "descs": {
            "4.3": {
                "en-US": "",
                "zh-CN": ""
            }
        },
        "image_path": "cardface/Char_Monster_DahakaIce.png",  # noqa: E501
    },
    "CHARACTOR/Azhdaha_ELECTRO": {
        "names": {
            "en-US": "Azhdaha·Electro",
            "zh-CN": "若陀龙王·雷"
        },
        "descs": {
            "4.3": {
                "en-US": "",
                "zh-CN": ""
            }
        },
        "image_path": "cardface/Char_Monster_DahakaElec.png",  # noqa: E501
    },
    "CHARACTOR/Azhdaha_PYRO": {
        "names": {
            "en-US": "Azhdaha·Pyro",
            "zh-CN": "若陀龙王·火"
        },
        "descs": {
            "4.3": {
                "en-US": "",
                "zh-CN": ""
            }
        },
        "image_path": "cardface/Char_Monster_DahakaFire.png",  # noqa: E501
    },
    "CHARACTOR/Azhdaha_HYDRO": {
        "names": {
            "en-US": "Azhdaha·Hydro",
            "zh-CN": "若陀龙王·水"
        },
        "descs": {
            "4.3": {
                "en-US": "",
                "zh-CN": ""
            }
        },
        "image_path": "cardface/Char_Monster_DahakaWater.png",  # noqa: E501
    },
    "SKILL_Azhdaha_NORMAL_ATTACK/Sundering Charge": {
        "names": {
            "en-US": "Sundering Charge",
            "zh-CN": "碎岩冲撞"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 2 Physical DMG.",
                "zh-CN": "造成2点物理伤害。"
            }
        }
    },
    "SKILL_Azhdaha_ELEMENTAL_SKILL/Frostspike Wave": {
        "names": {
            "en-US": "Frostspike Wave",
            "zh-CN": "霜刺破袭"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 3 Cryo DMG, and attach Stone Facets: Elemental Crystallization to this character.",  # noqa: E501
                "zh-CN": "造成3点冰元素伤害，此角色附属磐岩百相·元素凝晶。"
            }
        }
    },
    "SKILL_Azhdaha_ELEMENTAL_SKILL/Torrential Rebuke": {
        "names": {
            "en-US": "Torrential Rebuke",
            "zh-CN": "洪流重斥"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 3 Hydro DMG, and attach Stone Facets: Elemental Crystallization to this character.",  # noqa: E501
                "zh-CN": "造成3点水元素伤害，此角色附属磐岩百相·元素凝晶。"
            }
        }
    },
    "SKILL_Azhdaha_ELEMENTAL_SKILL/Blazing Rebuke": {
        "names": {
            "en-US": "Blazing Rebuke",
            "zh-CN": "炽焰重斥"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 3 Pyro DMG, and attach Stone Facets: Elemental Crystallization to this character.",  # noqa: E501
                "zh-CN": "造成3点火元素伤害，此角色附属磐岩百相·元素凝晶。"
            }
        }
    },
    "SKILL_Azhdaha_ELEMENTAL_SKILL/Thunderstorm Wave": {
        "names": {
            "en-US": "Thunderstorm Wave",
            "zh-CN": "霆雷破袭"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 3 Electro DMG, and attach Stone Facets: Elemental Crystallization to this character.",  # noqa: E501
                "zh-CN": "造成3点雷元素伤害，此角色附属磐岩百相·元素凝晶。"
            }
        }
    },
    "SKILL_Azhdaha_ELEMENTAL_SKILL/Aura of Majesty": {
        "names": {
            "en-US": "Aura of Majesty",
            "zh-CN": "磅礴之气"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 3 Geo DMG. If a Crystallize reaction occurs, then this character will perform Elemental Absorption.\nIf during the usage of this skill, the character hasn't absorbed an element's power yet, then Stone Facets: Elemental Crystallization will be attached.",  # noqa: E501
                "zh-CN": "造成3点岩元素伤害，如果发生了结晶反应，则角色汲取对应元素的力量。\n如果本技能中角色未汲取元素的力量，则附属磐岩百相·元素凝晶。"  # noqa: E501
            }
        }
    },
    "CHARACTOR_STATUS/Stone Facets: Elemental Crystallization": {
        "names": {
            "en-US": "Stone Facets: Elemental Crystallization",
            "zh-CN": "磐岩百相·元素凝晶"
        },
        "descs": {
            "4.3": {
                "en-US": "After this character takes Cryo/Hydro/Pyro/Electro DMG: If this character currently has not absorbed the power of this element, remove this effect, and then this character performs Elemental Absorption.",  # noqa: E501
                "zh-CN": "角色受到冰/水/火/雷元素伤害后：如果角色当前未汲取该元素的力量，则移除此状态，然后角色汲取对应元素的力量。"  # noqa: E501
            }
        },
        "image_path": "status/Dahaka_S.png"
    },
    "SKILL_Azhdaha_ELEMENTAL_BURST/Decimating Rockfall": {
        "names": {
            "en-US": "Decimating Rockfall",
            "zh-CN": "山崩毁阵"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 4 Geo DMG. DMG +1 for each element previously absorbed.",  # noqa: E501
                "zh-CN": "造成4点岩元素伤害，每汲取过一种元素此伤害+1。"
            }
        }
    },
    "SKILL_Azhdaha_PASSIVE/Stone Facets": {
        "names": {
            "en-US": "Stone Facets",
            "zh-CN": "磐岩百相"
        },
        "descs": {
            "4.3": {
                "en-US": "(Passive) When the battle begins, this character gains Stone Facets: Elemental Absorption.",  # noqa: E501
                "zh-CN": "【被动】战斗开始时，初始附属磐岩百相·元素汲取。"
            }
        }
    },
    "CHARACTOR_STATUS/Stone Facets: Elemental Absorption": {
        "names": {
            "en-US": "Stone Facets: Elemental Absorption",
            "zh-CN": "磐岩百相·元素汲取"
        },
        "descs": {
            "4.3": {
                "en-US": "The character can absorb the power of the Elements, including Cryo/Hydro/Pyro/Electro, and then based on the element absorbed, gain the skills Frostspike Wave/Torrential Rebuke/Blazing Rebuke/Thunderstorm Wave. (The character can only have one Elemental Type absorbed at once, and this status will record the Elemental Type previously absorbed)\nAfter this character absorbs an element of a different type than the currently absorbed element: Generate 1 Elemental Die of the same type as the Element that was just absorbed. The usages of this status represents the number of Elemental Types that the character has absorbed.",  # noqa: E501
                "zh-CN": "角色可以汲取冰/水/火/雷元素的力量，然后根据所汲取的元素类型，获得技能霜刺破袭/洪流重斥/炽焰重斥/霆雷破袭。（角色同时只能汲取一种元素，此状态会记录角色已汲取过的元素类型数量）\n角色汲取了一种和当前不同的元素后：生成1个所汲取元素类型的元素骰。该角色状态的可用次数代表角色汲取过的元素种类数。"  # noqa: E501
            }
        }
    },
    "TALENT_Azhdaha/Lunar Cycles Unending": {
        "names": {
            "en-US": "Lunar Cycles Unending",
            "zh-CN": "晦朔千引"
        },
        "descs": {
            "4.3": {
                "en-US": "Combat Action: When your active character is Azhdaha, play this to them. Attach Stone Facets: Elemental Crystallization to Azhdaha, then create 1 Elemental Die for each Elemental Type your characters have.\n(Deck must contain Azhdaha to add this card to it)",  # noqa: E501
                "zh-CN": "战斗行动：我方出战角色为若陀龙王时，对该角色打出。使若陀龙王附属磐岩百相·元素凝晶，然后生成每种我方角色所具有的元素类型的元素骰各1个。\n（牌组中包含若陀龙王，才能加入牌组）"  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Talent_Dahaka.png",  # noqa: E501
        "id": 226022
    },
}


register_class(
    Azhdaha_4_3 | StoneFacetsElementalAbsorption_4_3 
    | StoneFacetsElementalCrystallization_4_3 | LunarCyclesUnending_4_3,
    desc
)
