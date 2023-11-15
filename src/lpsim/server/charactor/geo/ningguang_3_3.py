from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...action import Actions
from ...struct import Cost

from ...consts import (
    ELEMENT_TO_DAMAGE_TYPE, DamageElementalType, DieColor, ElementType, 
    FactionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalNormalAttackBase, ElementalSkillBase, 
    CharactorBase, SkillTalent
)


# Skills


class JadeScreen(ElementalSkillBase):
    name: Literal['Jade Screen'] = 'Jade Screen'
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.GEO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.GEO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        return super().get_actions(match) + [
            self.create_team_status(self.name),
        ]


class Starshatter(ElementalBurstBase):
    name: Literal['Starshatter'] = 'Starshatter'
    damage: int = 6
    damage_type: DamageElementalType = DamageElementalType.GEO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.GEO,
        elemental_dice_number = 3,
        charge = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Check if Jade Screen exists. If so, change self.damage to 8.
        """
        status = match.player_tables[self.position.player_idx].team_status
        screen_exist: bool = False
        for s in status:
            if s.name == 'Jade Screen':
                screen_exist = True
                break
        if screen_exist:
            # temporary change damage to 8
            self.damage = 8
        ret = super().get_actions(match)
        self.damage = 6
        return ret


# Talents


class StrategicReserve_3_3(SkillTalent):
    name: Literal['Strategic Reserve']
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Ningguang'] = 'Ningguang'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.GEO,
        elemental_dice_number = 4,
    )
    skill: Literal['Jade Screen'] = 'Jade Screen'


# charactor base


class Ningguang_3_3(CharactorBase):
    name: Literal['Ningguang']
    version: Literal['3.3'] = '3.3'
    element: ElementType = ElementType.GEO
    max_hp: int = 10
    max_charge: int = 3
    skills: List[
        ElementalNormalAttackBase | JadeScreen | Starshatter
    ] = []
    faction: List[FactionType] = [
        FactionType.LIYUE
    ]
    weapon_type: WeaponType = WeaponType.CATALYST

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name = 'Sparkling Scatter',
                damage_type = ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost = ElementalNormalAttackBase.get_cost(self.element),
            ),
            JadeScreen(),
            Starshatter(),
        ]


register_class(Ningguang_3_3 | StrategicReserve_3_3)
