from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...action import Actions
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, 
    WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Skills


class FantasticVoyage(ElementalBurstBase):
    name: Literal['Fantastic Voyage'] = 'Fantastic Voyage'
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 4,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        return super().get_actions(match) + [
            self.create_team_status('Inspiration Field', {
                'talent_activated': self.is_talent_equipped(match)
            })
        ]


# Talents


class GrandExpectation_3_3(SkillTalent):
    name: Literal['Grand Expectation']
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Bennett'] = 'Bennett'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 4,
        charge = 2
    )
    skill: Literal['Fantastic Voyage'] = 'Fantastic Voyage'


# charactor base


class Bennett_3_3(CharactorBase):
    name: Literal['Bennett']
    version: Literal['3.3'] = '3.3'
    element: ElementType = ElementType.PYRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | ElementalSkillBase | FantasticVoyage
    ] = []
    faction: List[FactionType] = [
        FactionType.MONDSTADT
    ]
    weapon_type: WeaponType = WeaponType.SWORD

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Strike of Fortune',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            ElementalSkillBase(
                name = 'Passion Overload',
                damage_type = DamageElementalType.PYRO,
                cost = ElementalSkillBase.get_cost(self.element),
            ),
            FantasticVoyage(),
        ]


register_class(Bennett_3_3 | GrandExpectation_3_3)
