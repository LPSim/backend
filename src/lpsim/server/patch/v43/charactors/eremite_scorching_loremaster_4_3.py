from typing import Dict, List, Literal

from ....event import (
    ReceiveDamageEventArguments, RoundPrepareEventArguments, 
    UseSkillEventArguments
)
from .....utils.class_registry import register_class
from ....status.charactor_status.base import DefendCharactorStatus
from ....summon.base import AttackAndGenerateStatusSummonBase
from ....action import Actions, ChargeAction, CreateObjectAction
from ....match import Match
from ....struct import Cost
from ....consts import (
    ELEMENT_TO_DAMAGE_TYPE, DamageElementalType, DieColor, ElementType, 
    FactionType, ObjectPositionType, SkillType, WeaponType
)
from ....charactor.charactor_base import (
    CharactorBase, ElementalBurstBase, ElementalNormalAttackBase, 
    ElementalSkillBase, PassiveSkillBase, SkillBase, SkillTalent
)
from .....utils.desc_registry import DescDictType


class PyroScorpionGuardianStance_4_3(DefendCharactorStatus):
    name: Literal[
        'Pyro Scorpion: Guardian Stance'
    ] = 'Pyro Scorpion: Guardian Stance'
    version: Literal['4.3'] = '4.3'
    desc: Literal['', 'talent'] = ''

    # usage and max usage will be set by summon
    min_damage_to_trigger: int = 1
    max_in_one_time: int = 1


class SpiritOfOmenPyroScorpion_4_3(AttackAndGenerateStatusSummonBase):
    name: Literal[
        'Spirit of Omen: Pyro Scorpion'
    ] = 'Spirit of Omen: Pyro Scorpion'
    desc: Literal['', 'talent'] = ''
    version: Literal['4.3'] = '4.3'
    usage: int = 2
    max_usage: int = 2
    damage: int = 1
    damage_elemental_type: DamageElementalType = DamageElementalType.PYRO
    status_name: str = 'Pyro Scorpion: Guardian Stance'

    def renew(self, obj: 'SpiritOfOmenPyroScorpion_4_3') -> None:
        super().renew(obj)
        if obj.desc == 'talent' and self.desc != 'talent':
            self.desc = 'talent'

    def _create_status(self, match: Match) -> List[CreateObjectAction]:
        """
        Create for eremite self
        """
        charactors = match.player_tables[self.position.player_idx].charactors
        for c in charactors:
            if c.name == 'Eremite Scorching Loremaster':
                usage = 1
                if self.desc == 'talent':
                    usage = 2
                return [
                    CreateObjectAction(
                        object_name = 'Pyro Scorpion: Guardian Stance',
                        object_position = c.position.set_area(
                            ObjectPositionType.CHARACTOR_STATUS),
                        object_arguments = {
                            'desc': self.desc,
                            'usage': usage,
                            'max_usage': usage,
                        }
                    )
                ]
        else:
            raise AssertionError('Eremite Scorching Loremaster not found')

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Match
    ) -> List[CreateObjectAction]:
        """
        Reset damage and call super
        """
        self.damage = 1
        return super().event_handler_ROUND_PREPARE(event, match)

    def event_handler_USE_SKILL(
        self, event: UseSkillEventArguments, match: Match
    ) -> List[Actions]:
        """
        If talent activated, and self eremite use normal or elemental skill,
        damage be 2.
        """
        if self.desc != 'talent':
            # not talent, do nothing
            return []
        skill_position = event.action.skill_position
        if skill_position.player_idx != self.position.player_idx:
            # not self charactor use skill, do nothing
            return []
        charactor = match.player_tables[skill_position.player_idx].charactors[
            skill_position.charactor_idx]
        if charactor.name != 'Eremite Scorching Loremaster':
            # not eremite use skill, do nothing
            return []
        skill: SkillBase = match.get_object(skill_position)  # type: ignore
        assert skill is not None
        if (
            skill.skill_type == SkillType.NORMAL_ATTACK
            or skill.skill_type == SkillType.ELEMENTAL_SKILL
        ):
            # is self eremite use normal or elemental skill, damage be 2
            self.damage = 2
        return []


class SpiritOfOmensAwakeningPyroScorpion(ElementalBurstBase):
    name: Literal[
        'Spirit of Omen\'s Awakening: Pyro Scorpion'
    ] = 'Spirit of Omen\'s Awakening: Pyro Scorpion'
    damage: int = 2
    damage_type: Literal[DamageElementalType.PYRO] = DamageElementalType.PYRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 3,
        charge = 2
    )

    def get_actions(self, match: Match) -> List[Actions]:
        summon_desc = ''
        if self.is_talent_equipped(match):
            summon_desc = 'talent'
        return super().get_actions(match, [
            self.create_summon('Spirit of Omen: Pyro Scorpion', {
                'desc': summon_desc
            })
        ])


class SpiritOfOmensPower(PassiveSkillBase):
    name: Literal['Spirit of Omen\'s Power'] = 'Spirit of Omen\'s Power'
    triggered: bool = False

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Match
    ) -> List[ChargeAction]:
        """
        When self receive damage, and self alive, and self hp <= 7,
        and not triggered, gain 1 charge
        """
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        if not event.final_damage.is_corresponding_charactor_receive_damage(
            charactor.position, match, ignore_piercing = False
        ):
            # not self receive damage, do nothing
            return []
        if charactor.is_defeated:  # pragma: no cover
            # self defeated, do nothing
            return []
        if charactor.hp > 7:
            # self hp > 7, do nothing
            return []
        if self.triggered:
            # already triggered, do nothing
            return []
        self.triggered = True
        return [ ChargeAction(
            player_idx = charactor.position.player_idx,
            charactor_idx = charactor.position.charactor_idx,
            charge = 1
        )]


class Scorpocalypse_4_3(SkillTalent):
    name: Literal['Scorpocalypse'] = 'Scorpocalypse'
    version: Literal['4.3'] = '4.3'
    charactor_name: Literal[
        'Eremite Scorching Loremaster'
    ] = 'Eremite Scorching Loremaster'
    skill: Literal[
        'Spirit of Omen\'s Awakening: Pyro Scorpion'
    ] = 'Spirit of Omen\'s Awakening: Pyro Scorpion'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 3,
        charge = 2
    )


class EremiteScorchingLoremaster_4_3(CharactorBase):
    name: Literal[
        'Eremite Scorching Loremaster'
    ] = 'Eremite Scorching Loremaster'
    version: Literal['4.3'] = '4.3'
    element: ElementType = ElementType.PYRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        ElementalNormalAttackBase | ElementalSkillBase 
        | SpiritOfOmensAwakeningPyroScorpion | SpiritOfOmensPower
    ] = []
    faction: List[FactionType] = [FactionType.THE_EREMITES]
    weapon_type: WeaponType = WeaponType.OTHER

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name = 'Searing Glare',
                damage_type = ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost = ElementalNormalAttackBase.get_cost(self.element),
            ),
            ElementalSkillBase(
                name = 'Blazing Strike',
                damage_type = ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost = ElementalSkillBase.get_cost(self.element),
            ),
            SpiritOfOmensAwakeningPyroScorpion(),
            SpiritOfOmensPower(),
        ]


desc: Dict[str, DescDictType] = {
    "CHARACTOR/Eremite Scorching Loremaster": {
        "names": {
            "en-US": "Eremite Scorching Loremaster",
            "zh-CN": "镀金旅团·炽沙叙事人"
        },
        "image_path": "cardface/Char_Monster_Muscleman.png",  # noqa: E501
        "id": 2303,
        "descs": {
            "4.3": {
                "en-US": "",
                "zh-CN": ""
            }
        }
    },
    "SKILL_Eremite Scorching Loremaster_NORMAL_ATTACK/Searing Glare": {
        "names": {
            "en-US": "Searing Glare",
            "zh-CN": "烧蚀之光"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 1 Pyro DMG.",
                "zh-CN": "造成1点火元素伤害。"
            }
        }
    },
    "SKILL_Eremite Scorching Loremaster_ELEMENTAL_SKILL/Blazing Strike": {
        "names": {
            "en-US": "Blazing Strike",
            "zh-CN": "炎晶迸击"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 3 Pyro DMG.",
                "zh-CN": "造成3点火元素伤害。"
            }
        }
    },
    "SKILL_Eremite Scorching Loremaster_ELEMENTAL_BURST/Spirit of Omen's Awakening: Pyro Scorpion": {  # noqa: E501
        "names": {
            "en-US": "Spirit of Omen's Awakening: Pyro Scorpion",
            "zh-CN": "厄灵苏醒·炎之魔蝎"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 2 Pyro DMG, summons 1 Spirit of Omen: Pyro Scorpion.",  # noqa: E501
                "zh-CN": "造成2点火元素伤害，召唤厄灵·炎之魔蝎。"
            }
        }
    },
    "SUMMON/Spirit of Omen: Pyro Scorpion": {
        "names": {
            "en-US": "Spirit of Omen: Pyro Scorpion",
            "zh-CN": "厄灵·炎之魔蝎"
        },
        "descs": {
            "4.3": {
                "en-US": "End Phase: Deal 1 Pyro DMG.\nUsage(s): 2\n\nWhen entering play, when the Action Phase starts: Equips Pyro Scorpion: Guardian Stance to your Eremite Scorching Loremaster. (When Spirit of Omen: Pyro Scorpion is in play, the character will take 1 less DMG, once per Round.)",  # noqa: E501
                "zh-CN": "结束阶段：造成1点火元素伤害。\n可用次数：2\n\n入场时和行动阶段开始：使我方镀金旅团·炽沙叙事人附属炎之魔蝎·守势。（厄灵·炎之魔蝎在场时每回合1次，使角色受到的伤害-1。）"  # noqa: E501
            }
        }
    },
    "SUMMON/Spirit of Omen: Pyro Scorpion_talent": {
        "names": {
            "en-US": "Spirit of Omen: Pyro Scorpion",
            "zh-CN": "厄灵·炎之魔蝎"
        },
        "descs": {
            "4.3": {
                "en-US": "End Phase: Deal 1 Pyro DMG; in Rounds when Eremite Scorching Loremaster has used a Normal Attack or Elemental Skill, the damage dealt +1.\nUsage(s): 2\n\nWhen entering play, when the Action Phase starts: Equips Pyro Scorpion: Guardian Stance to your Eremite Scorching Loremaster. (When Spirit of Omen: Pyro Scorpion is in play, the character will take 1 less DMG, twice per Round.)",  # noqa: E501
                "zh-CN": "结束阶段：造成1点火元素伤害；在镀金旅团·炽沙叙事人使用过「普通攻击」或「元素战技」的回合中，造成的伤害+1。\n可用次数：2\n\n入场时和行动阶段开始：使我方镀金旅团·炽沙叙事人附属炎之魔蝎·守势。（厄灵·炎之魔蝎在场时每回合2次，使角色受到的伤害-1。）"  # noqa: E501
            }
        }
    },
    "CHARACTOR_STATUS/Pyro Scorpion: Guardian Stance": {
        "names": {
            "en-US": "Pyro Scorpion: Guardian Stance",
            "zh-CN": "炎之魔蝎·守势"
        },
        "descs": {
            "4.3": {
                "en-US": "the character will take 1 less DMG, once per Round.",  # noqa: E501
                "zh-CN": "使角色受到的伤害-1，每回合1次。"
            },
        },
    },
    "CHARACTOR_STATUS/Pyro Scorpion: Guardian Stance_talent": {
        "names": {
            "en-US": "Pyro Scorpion: Guardian Stance",
            "zh-CN": "炎之魔蝎·守势"
        },
        "descs": {
            "4.3": {
                "en-US": "the character will take 1 less DMG, twice per Round.",  # noqa: E501
                "zh-CN": "使角色受到的伤害-1，每回合2次。"
            },
        },
    },
    "SKILL_Eremite Scorching Loremaster_PASSIVE/Spirit of Omen's Power": {
        "names": {
            "en-US": "Spirit of Omen's Power",
            "zh-CN": "厄灵之能"
        },
        "descs": {
            "4.3": {
                "en-US": "(Passive) After this character takes DMG: If this character has no greater than 7 HP, they gain 1 Energy. (Once per Match)",  # noqa: E501
                "zh-CN": "【被动】此角色受到伤害后：如果此角色生命值不多于7，则获得1点充能。（整场牌局限制1次）"  # noqa: E501
            }
        }
    },
    "TALENT_Eremite Scorching Loremaster/Scorpocalypse": {
        "names": {
            "en-US": "Scorpocalypse",
            "zh-CN": "魔蝎烈祸"
        },
        "descs": {
            "4.3": {
                "en-US": "Combat Action: When your active character is Eremite Scorching Loremaster, equip this card.\nAfter Eremite Scorching Loremaster equips this card, immediately use Spirit of Omen's Awakening: Pyro Scorpion once.\nSpirit of Omen: Pyro Scorpion created by Eremite Scorching Loremaster with this card equipped will deal +1 DMG in Rounds when Eremite Scorching Loremaster has used a Normal Attack or Elemental Skill.\nSpirit of Omen: Pyro Scorpion's DMG reduction effect can now be triggered twice per Round.\n(Your deck must contain Eremite Scorching Loremaster to add this card to it)",  # noqa: E501
                "zh-CN": "战斗行动：我方出战角色为镀金旅团·炽沙叙事人时，装备此牌。\n镀金旅团·炽沙叙事人装备此牌后，立刻使用一次厄灵苏醒·炎之魔蝎。\n装备有此牌的镀金旅团·炽沙叙事人生成的厄灵·炎之魔蝎在镀金旅团·炽沙叙事人使用过「普通攻击」或「元素战技」的回合中，造成的伤害+1；\n厄灵·炎之魔蝎的减伤效果改为每回合至多2次。\n（牌组中包含镀金旅团·炽沙叙事人，才能加入牌组）"  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Talent_Muscleman.png",  # noqa: E501
        "id": 223031
    },
}


register_class(
    PyroScorpionGuardianStance_4_3 | SpiritOfOmenPyroScorpion_4_3
    | Scorpocalypse_4_3 | EremiteScorchingLoremaster_4_3, desc
)
