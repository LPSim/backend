from typing import List, Literal, Any

from ....utils.class_registry import register_class

from ...event import SkillEndEventArguments

from ...action import Actions, MakeDamageAction
from ...consts import (
    ElementType, FactionType, SkillType, WeaponType, DamageElementalType,
    DamageType, DieColor
)
from ..charactor_base import (
    AOESkillBase, PhysicalNormalAttackBase, ElementalSkillBase, 
    ElementalBurstBase, CharactorBase, SkillTalent
)
from ...struct import Cost
from ...modifiable_values import DamageValue
from ...summon.base import AttackerSummonBase


class Nightrider(ElementalSkillBase):
    name: Literal['Nightrider'] = 'Nightrider'
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3,
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return super().get_actions(match) + [self.create_summon('Oz')]


class MidnightPhantasmagoria(ElementalBurstBase, AOESkillBase):
    name: Literal['Midnight Phantasmagoria'] = 'Midnight Phantasmagoria'
    damage: int = 4
    damage_type: DamageElementalType = DamageElementalType.ELECTRO
    back_damage: int = 2
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3,
        charge = 3,
    )


class StellarPredator_3_3(SkillTalent):
    name: Literal['Stellar Predator']
    charactor_name: Literal['Fischl'] = 'Fischl'
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.ELECTRO,
        elemental_dice_number = 3,
    )
    skill: Literal['Nightrider'] = 'Nightrider'


class Oz_3_3(AttackerSummonBase):
    name: Literal['Oz']
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.ELECTRO
    damage: int = 1
    renew_type: Literal['RESET_WITH_MAX'] = 'RESET_WITH_MAX'

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        If Fischl made normal attack and with talent, make 2 electro damage 
        to front.
        """
        action = event.action
        if action.skill_type != SkillType.NORMAL_ATTACK:
            # not using normal attack
            return []
        if self.position.player_idx != action.position.player_idx:
            # not attack by self
            return []
        charactor = match.player_tables[action.position.player_idx].charactors[
            action.position.charactor_idx
        ]
        if (
            charactor.talent is not None and charactor.name == 'Fischl'
            and charactor.talent.name == 'Stellar Predator'
        ):
            # match, decrease usage, attack.
            # after make damage, will trigger usage check, so no need to
            # add RemoveObjectAction here.
            assert self.usage > 0
            self.usage -= 1
            target_table = match.player_tables[1 - self.position.player_idx]
            target_charactor = target_table.charactors[
                target_table.active_charactor_idx
            ]
            return [
                MakeDamageAction(
                    damage_value_list = [
                        DamageValue(
                            position = self.position,
                            damage_type = DamageType.DAMAGE,
                            target_position = target_charactor.position,
                            damage = 2,
                            damage_elemental_type = self.damage_elemental_type,
                            cost = Cost()
                        )
                    ],
                )
            ]
        return []


class Fischl_3_3(CharactorBase):
    name: Literal['Fischl']
    version: Literal['3.3'] = '3.3'
    element: ElementType = ElementType.ELECTRO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        PhysicalNormalAttackBase | Nightrider | MidnightPhantasmagoria
    ] = []
    faction: List[FactionType] = [
        FactionType.MONDSTADT,
    ]
    weapon_type: WeaponType = WeaponType.BOW

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Bolts of Downfall',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            Nightrider(),
            MidnightPhantasmagoria(),
        ]


register_class(Fischl_3_3 | Oz_3_3 | StellarPredator_3_3)
