from typing import Literal
from pydantic import validator
from ..object_base import (
    ElementalNormalAttackBase,
    ElementalSkillBase, ElementalBurstBase
)
from ..consts import (
    ElementType, FactionType, WeaponType,
    ELEMENT_TO_DAMAGE_TYPE
)
from .mob import Mob
from .charactor_base import CharactorBase


class MobMage(Mob):
    """
    Mob mages. They cannot carry weapons in default. Their normal 
    attacks are 2 physical DMG, elemental skills are 3 element DMG, 
    elemental bursts are 2 charges, 3 cost, and 5 element DMG.
    Their names should be BlablaMob, here Blabla should be one of elemental
    types.
    """
    name: Literal[
        'CryoMobMage',
        'HydroMobMage',
        'PyroMobMage',
        'ElectroMobMage',
        'GeoMobMage',
        'DendroMobMage',
        'AnemoMobMage',
    ]
    version = '1.0.0'
    element: ElementType = ElementType.NONE
    hp: int = 10
    max_hp: int = 10
    charge: int = 0
    max_charge: int = 2
    skills: list[
        ElementalNormalAttackBase | ElementalSkillBase | ElementalBurstBase
    ] = []
    faction: list[FactionType] = []
    weapon_type: WeaponType = WeaponType.CATALYST

    @validator('element')
    def element_fits_name(cls, v: ElementType, values, **kwargs):
        """
        Check if element type fits name.
        """
        if 'name' not in values:
            raise ValueError('Name not found.')
        type_in_name: str = values['name'][:-7].upper()
        element_type: str = v.value
        if type_in_name != element_type:
            raise ValueError(
                f'Element type {element_type} does not fit '
                f'name {type_in_name}.'
            )
        return v

    def __init__(self, **kwargs):
        super(CharactorBase, self).__init__(**kwargs)  # type: ignore
        if self.element == ElementType.NONE:
            # set element by name
            element_name = self.name[:-7].upper()
            self.element = ElementType(element_name)
        element_name = self.element.value.lower()
        element_name = element_name[0].upper() + element_name[1:]
        normal_attack = ElementalNormalAttackBase(
            name = f'{element_name} Normal Attack',
            damage_type = ELEMENT_TO_DAMAGE_TYPE[self.element],
            cost = ElementalNormalAttackBase.get_cost(self.element),
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
        self.desc = self.desc.replace('_NAME_', self.name)
