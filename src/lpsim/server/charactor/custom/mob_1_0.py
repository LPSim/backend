from typing import List, Literal
from pydantic import validator

from ....utils.class_registry import register_class
from ...consts import (
    ElementType, FactionType, WeaponType, DamageElementalType,
    ELEMENT_TO_DAMAGE_TYPE
)
from ..charactor_base import (
    PhysicalNormalAttackBase, ElementalSkillBase, ElementalBurstBase, 
    CharactorBase
)


class Mob_1_0(CharactorBase):
    """
    Mobs. They cannot carry weapons in default. Their normal 
    attacks are 2 physical DMG, elemental skills are 3 element DMG, 
    elemental bursts are 2 charges, 3 cost, and 5 element DMG.
    Their names should be BlablaMob, here Blabla should be one of elemental
    types.
    """
    name: Literal[
        'CryoMob',
        'HydroMob',
        'PyroMob',
        'ElectroMob',
        'GeoMob',
        'DendroMob',
        'AnemoMob',
    ]
    version: Literal['1.0'] = '1.0'
    element: ElementType = ElementType.NONE
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | ElementalSkillBase | ElementalBurstBase
    ] = []
    faction: List[FactionType] = []
    weapon_type: WeaponType = WeaponType.OTHER

    @validator('element')
    def element_fits_name(cls, v: ElementType, values, **kwargs):
        """
        Check if element type fits name.
        """
        if 'name' not in values:
            raise AssertionError('Name not found.')
        type_in_name: str = values['name'][:-3].upper()
        element_type: str = v.value
        if type_in_name != element_type:
            raise ValueError(
                f'Element type {element_type} does not fit '
                f'name {type_in_name}.'
            )
        return v

    def _init_skills(self):
        if self.element == ElementType.NONE:
            # set element by name
            element_name = self.name[:-3].upper()
            self.element = ElementType(element_name)
        element_name = self.element.value.lower()
        element_name = element_name[0].upper() + element_name[1:]
        normal_attack = PhysicalNormalAttackBase(
            name = 'Physical Normal Attack',
            damage_type = DamageElementalType.PHYSICAL,
            cost = PhysicalNormalAttackBase.get_cost(self.element),
        )
        elemental_skill = ElementalSkillBase(
            name = f'{element_name} Elemental Skill',
            damage_type = ELEMENT_TO_DAMAGE_TYPE[self.element],
            cost = ElementalSkillBase.get_cost(self.element),
        )
        elemental_burst = ElementalBurstBase(
            name = f'{element_name} Elemental Burst',
            damage_type = ELEMENT_TO_DAMAGE_TYPE[self.element],
            cost = ElementalBurstBase.get_cost(self.element, 3, 2),
            damage = 5,
        )
        self.skills = [normal_attack, elemental_skill, elemental_burst]


register_class(Mob_1_0)
