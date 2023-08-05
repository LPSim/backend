from typing import Literal
from ..object_base import (
    PhysicalNormalAttackBase,
    ElementalSkillBase, ElementalBurstBase
)
from ..consts import (
    ElementType, FactionType, WeaponType, DamageType,
)
from .charactor_base import CharactorBase


class PhysicalMob(CharactorBase):
    """
    Physical mobs. They cannot carry weapons in default. Their normal 
    attacks are 2 physical DMG, elemental skills are 3 physical DMG, 
    elemental bursts are 2 charges, 3 cost, and 5 physical DMG.
    Their elemeny type is only used to decide dice color when using skills.
    """
    name: Literal['PhysicalMob']
    version = '1.0.0'
    element: ElementType
    hp: int = 10
    max_hp: int = 10
    charge: int = 0
    max_charge: int = 2
    skills: list[
        PhysicalNormalAttackBase | ElementalSkillBase | ElementalBurstBase
    ] = []
    faction: list[FactionType] = []
    weapon_type: WeaponType = WeaponType.OTHER

    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # type: ignore
        element_name = self.element.value.lower()
        element_name = element_name[0].upper() + element_name[1:]
        normal_attack = PhysicalNormalAttackBase(
            name = 'Physical Normal Attack',
            damage_type = DamageType.PHYSICAL,
            cost = PhysicalNormalAttackBase.get_cost(self.element),
        )
        elemental_skill = ElementalSkillBase(
            name = 'Physical Skill',
            damage_type = DamageType.PHYSICAL,
            cost = ElementalSkillBase.get_cost(self.element),
        )
        elemental_burst = ElementalBurstBase(
            name = 'Physical Burst',
            damage_type = DamageType.PHYSICAL,
            cost = ElementalBurstBase.get_cost(self.element, 3),
            damage = 5,
            charge = 2
        )
        self.skills = [normal_attack, elemental_skill, elemental_burst]
