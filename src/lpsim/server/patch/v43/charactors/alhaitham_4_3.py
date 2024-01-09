from typing import Dict, List, Literal

from .....utils.class_registry import register_class
from ....modifiable_values import DamageValue
from ....event import SkillEndEventArguments
from ....status.charactor_status.base import (
    ElementalInfusionCharactorStatus, RoundCharactorStatus
)
from ....action import (
    Actions, ChangeObjectUsageAction, DrawCardAction, MakeDamageAction, 
    RemoveObjectAction
)
from ....match import Match
from ....struct import Cost
from ....consts import (
    DamageElementalType, DamageType, DieColor, ElementType, FactionType, 
    IconType, SkillType, WeaponType
)
from ....charactor.charactor_base import (
    CharactorBase, ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, SkillBase, SkillTalent
)
from .....utils.desc_registry import DescDictType


class ChiselLightMirror_4_3(ElementalInfusionCharactorStatus, 
                            RoundCharactorStatus):
    name: Literal["Chisel-Light Mirror"] = "Chisel-Light Mirror"
    version: Literal['4.3'] = '4.3'
    usage: int = 2
    max_usage: int = 3

    infused_elemental_type: DamageElementalType = DamageElementalType.DENDRO
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Match
    ) -> List[MakeDamageAction | ChangeObjectUsageAction]:
        """
        When self normal attack, deal 1 dendro damage. If is charged attack,
        duration +1.
        """
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            charactor_idx_same = True
        ):
            # not self skill
            return []
        skill: SkillBase = match.get_object(event.action.position)  # type: ignore  # noqa: E501
        assert skill is not None
        if skill.skill_type != SkillType.NORMAL_ATTACK:
            # not normal attack
            return []
        target = match.player_tables[
            1 - self.position.player_idx].get_active_charactor()
        ret: List[MakeDamageAction | ChangeObjectUsageAction] = [
            MakeDamageAction(
                damage_value_list = [
                    DamageValue(
                        position = self.position,
                        damage_type = DamageType.DAMAGE,
                        target_position = target.position,
                        damage = 1,
                        damage_elemental_type = DamageElementalType.DENDRO,
                        cost = Cost(),
                    )
                ]
            ),
        ]
        if (
            match.player_tables[self.position.player_idx].charge_satisfied
            and self.usage < self.max_usage
        ):
            # is charged attack and self usage not full
            ret.append(
                ChangeObjectUsageAction(
                    object_position = self.position,
                    change_usage = 1
                )
            )
        return ret


class UniversalityAnElaborationOnForm(ElementalSkillBase):
    name: Literal[
        "Universality: An Elaboration on Form"
    ] = "Universality: An Elaboration on Form"
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.DENDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.DENDRO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Match) -> List[Actions]:
        return super().get_actions(match, [
            self.create_charactor_status('Chisel-Light Mirror')
        ])


class ParticularFieldFettersOfPhenomena(ElementalBurstBase):
    name: Literal[
        "Particular Field: Fetters of Phenomena"
    ] = "Particular Field: Fetters of Phenomena"
    damage: int = 4
    damage_type: DamageElementalType = DamageElementalType.DENDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.DENDRO,
        elemental_dice_number = 3,
        charge = 2
    )

    def get_actions(self, match: Match) -> List[Actions]:
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        status = None
        for s in charactor.status:
            if s.name == 'Chisel-Light Mirror':
                status = s
                break
        if status is None:
            # attack and create 3-stack status
            return super().get_actions(match, [
                self.create_charactor_status(
                    'Chisel-Light Mirror',
                    { 'usage': 3 }
                )
            ])
        else:
            # attack and change status usage
            has_talent = self.is_talent_equipped(match)
            new_usage = 3 - status.usage
            if has_talent:
                new_usage = 3
            delta_usage = new_usage - status.usage
            self.damage += status.usage
            ret = super().get_actions(match)
            self.damage -= status.usage
            if new_usage > 0:
                # change usage
                ret.append(ChangeObjectUsageAction(
                    object_position = status.position,
                    change_usage = delta_usage
                ))
            if new_usage == 0:
                # remove status
                ret.append(RemoveObjectAction(
                    object_position = status.position
                ))
            if has_talent:
                # draw 1 card
                ret.append(DrawCardAction(
                    player_idx = self.position.player_idx,
                    number = 1,
                    draw_if_filtered_not_enough = True
                ))
            return ret


class Structuration_4_3(SkillTalent):
    name: Literal["Structuration"] = "Structuration"
    version: Literal['4.3'] = '4.3'
    charactor_name: Literal["Alhaitham"] = "Alhaitham"
    skill: Literal[
        "Particular Field: Fetters of Phenomena"
    ] = "Particular Field: Fetters of Phenomena"
    cost: Cost = Cost(
        elemental_dice_color = DieColor.DENDRO,
        elemental_dice_number = 3,
        charge = 2
    )


class Alhaitham_4_3(CharactorBase):
    name: Literal["Alhaitham"]
    version: Literal['4.3'] = '4.3'
    element: ElementType = ElementType.DENDRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | UniversalityAnElaborationOnForm 
        | ParticularFieldFettersOfPhenomena
    ] = []
    faction: List[FactionType] = [
        FactionType.SUMERU
    ]
    weapon_type: WeaponType = WeaponType.SWORD

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Abductive Reasoning',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            UniversalityAnElaborationOnForm(),
            ParticularFieldFettersOfPhenomena(),
        ]


desc: Dict[str, DescDictType] = {
    "CHARACTOR/Alhaitham": {
        "names": {
            "en-US": "Alhaitham",
            "zh-CN": "艾尔海森"
        },
        "image_path": "cardface/Char_Avatar_Alhatham.png",  # noqa: E501
        "id": 1706,
        "descs": {
            "4.3": {
                "en-US": "",
                "zh-CN": ""
            }
        }
    },
    "SKILL_Alhaitham_NORMAL_ATTACK/Abductive Reasoning": {
        "names": {
            "en-US": "Abductive Reasoning",
            "zh-CN": "溯因反绎法"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 2 Physical DMG.",
                "zh-CN": "造成2点物理伤害。"
            }
        }
    },
    "SKILL_Alhaitham_ELEMENTAL_SKILL/Universality: An Elaboration on Form": {
        "names": {
            "en-US": "Universality: An Elaboration on Form",
            "zh-CN": "共相·理式摹写"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 2 Dendro DMG. This character gains Chisel-Light Mirror.",  # noqa: E501
                "zh-CN": "造成2点草元素伤害，本角色附属琢光镜。"
            }
        }
    },
    "CHARACTOR_STATUS/Chisel-Light Mirror": {
        "names": {
            "en-US": "Chisel-Light Mirror",
            "zh-CN": "琢光镜"
        },
        "descs": {
            "4.3": {
                "en-US": "Physical DMG dealt by the character is converted to Dendro DMG.\nAfter this character performs a Normal Attack: Deals 1 Dendro DMG. If this Skill is a Charged Attack, this state's Duration (Rounds) +1.\nDuration (Rounds): 2 (Can stack, max 3 stacks)",  # noqa: E501
                "zh-CN": "角色造成的物理伤害变为草元素伤害。\n角色普通攻击后：造成1点草元素伤害。如果此技能为重击，则使此状态的持续回合+1。\n持续回合：2（可叠加，最多叠加到3回合）"  # noqa: E501
            }
        },
        "image_path": "status/Alhatham_S.png"
    },
    "SKILL_Alhaitham_ELEMENTAL_BURST/Particular Field: Fetters of Phenomena": {
        "names": {
            "en-US": "Particular Field: Fetters of Phenomena",
            "zh-CN": "殊境·显像缚结"
        },
        "descs": {
            "4.3": {
                "en-US": "Deals 4 Dendro DMG, consumes Chisel-Light Mirror, with the DMG bonus based on Chisel-Light Mirror's Duration (Rounds) consumed.\nIf Chisel-Light Mirror Duration (Rounds) consumed is 0/1/2, then apply Chisel-Light Mirror with 3/2/1 Duration (Rounds) to this character.",  # noqa: E501
                "zh-CN": "造成4点草元素伤害；消耗琢光镜，此伤害提升所消耗琢光镜的持续回合值。\n如果消耗琢光镜的持续回合为0/1/2，则为角色附属持续回合为3/2/1的琢光镜。"  # noqa: E501
            }
        }
    },
    "TALENT_Alhaitham/Structuration": {
        "names": {
            "en-US": "Structuration",
            "zh-CN": "正理"
        },
        "descs": {
            "4.3": {
                "en-US": "Combat Action: When your active character is Alhaitham, equip this card.\nAfter Alhaitham equips this card, immediately use Particular Field: Fetters of Phenomena once.\nWhen your Alhaitham, who has this card equipped, uses Particular Field: Fetters of Phenomena, if you expended at least 1 Duration (Rounds) of Chisel-Light Mirror, attach Chisel-Light Mirror with 3 Duration (Rounds) and draw 1 card.\n(You must have Alhaitham in your deck to add this card to your deck.)",  # noqa: E501
                "zh-CN": "战斗行动：我方出战角色为艾尔海森时，装备此牌。\n艾尔海森装备此牌后，立刻使用一次殊境·显像缚结。\n装备有此牌的艾尔海森使用殊境·显像缚结时：如果消耗了持续回合至少为1的琢光镜，则总是附属持续回合为3的琢光镜，并且抓1张牌。\n（牌组中包含艾尔海森，才能加入牌组）"  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Constellation_Alhatham.png",  # noqa: E501
        "id": 217061
    },
}


register_class(
    ChiselLightMirror_4_3 | Structuration_4_3 | Alhaitham_4_3, desc
)
