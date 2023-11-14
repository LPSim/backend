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
    CharactorBase, PhysicalNormalAttackBase, SkillTalent
)


class Breastplate(ElementalSkillBase):
    name: Literal['Breastplate'] = 'Breastplate'
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.GEO
    cost: Cost = Cost(
        elemental_dice_number = 3,
        elemental_dice_color = DieColor.GEO
    )

    def get_actions(self, match: Any) -> List[Actions]:
        ret = super().get_actions(match)
        ret.append(self.create_team_status('Full Plate'))
        return ret


class SweepingTime(ElementalBurstBase):
    name: Literal['Sweeping Time'] = 'Sweeping Time'
    damage: int = 4
    damage_type: DamageElementalType = DamageElementalType.GEO
    cost: Cost = Cost(
        elemental_dice_number = 4,
        elemental_dice_color = DieColor.GEO,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        ret = super().get_actions(match)
        ret.append(self.create_charactor_status('Sweeping Time'))
        return ret


class IGotYourBack_3_3(SkillTalent):
    name: Literal['I Got Your Back']
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Noelle'] = 'Noelle'
    cost: Cost = Cost(
        elemental_dice_number = 3,
        elemental_dice_color = DieColor.GEO
    )
    skill: Literal['Breastplate'] = 'Breastplate'


class Noelle_3_3(CharactorBase):
    name: Literal['Noelle']
    version: Literal['3.3'] = '3.3'
    element: ElementType = ElementType.GEO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | Breastplate | SweepingTime
    ] = []
    faction: List[FactionType] = [
        FactionType.MONDSTADT
    ]
    weapon_type: WeaponType = WeaponType.CLAYMORE

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Favonius Bladework - Maid',
                cost = PhysicalNormalAttackBase.get_cost(
                    ElementType.GEO,
                )
            ),
            Breastplate(),
            SweepingTime()
        ]


register_class(Noelle_3_3 | IGotYourBack_3_3)
