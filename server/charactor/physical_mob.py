from typing import List, Literal
from ..consts import (
    ElementType, FactionType, WeaponType, DamageElementalType,
)
from .charactor_base import (
    PhysicalNormalAttackBase, ElementalSkillBase, ElementalBurstBase, 
    CharactorBase
)


class PhysicalMob(CharactorBase):
    """
    Physical mobs. They cannot carry weapons in default. Their normal 
    attacks are 2 physical DMG, elemental skills are 3 physical DMG, 
    elemental bursts are 2 charges, 3 cost, and 5 physical DMG.
    Their elemeny type is only used to decide dice color when using skills.
    """
    name: Literal['PhysicalMob']
    desc: str = 'A PhysicalMob.'
    version: Literal['1.0'] = '1.0'
    element: ElementType = ElementType.PYRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | ElementalSkillBase | ElementalBurstBase
    ] = []
    faction: List[FactionType] = []
    weapon_type: WeaponType = WeaponType.OTHER

    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # type: ignore

    def _init_skills(self):
        element_name = self.element.value.lower()
        element_name = element_name[0].upper() + element_name[1:]
        normal_attack = PhysicalNormalAttackBase(
            name = 'Physical Normal Attack',
            damage_type = DamageElementalType.PHYSICAL,
            cost = PhysicalNormalAttackBase.get_cost(self.element),
        )
        elemental_skill = ElementalSkillBase(
            name = 'Physical Skill',
            damage_type = DamageElementalType.PHYSICAL,
            cost = ElementalSkillBase.get_cost(self.element),
        )
        elemental_burst = ElementalBurstBase(
            name = 'Physical Burst',
            damage_type = DamageElementalType.PHYSICAL,
            cost = ElementalBurstBase.get_cost(self.element, 3, 2),
            damage = 5,
        )
        self.skills = [normal_attack, elemental_skill, elemental_burst]
