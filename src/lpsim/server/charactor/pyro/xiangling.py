from typing import Any, List, Literal

from ..old_version.talent_cards_4_2 import Crossfire_3_3

from ...summon.base import AttackerSummonBase

from ...action import Actions
from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Summons


class Guoba(AttackerSummonBase):
    name: Literal['Guoba'] = 'Guoba'
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.PYRO
    damage: int = 2


# Skills


class DoughFu(PhysicalNormalAttackBase):
    name: Literal['Dough-Fu'] = 'Dough-Fu'
    cost: Cost = PhysicalNormalAttackBase.get_cost(ElementType.PYRO)


class GuobaAttack(ElementalSkillBase):
    name: Literal['Guoba Attack'] = 'Guoba Attack'
    desc: str = '''Summons 1 Guoba.'''
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        ret: List[Actions] = []
        if self.is_talent_equipped(match):
            ret = super().get_actions(match)
        ret.append(self.create_summon('Guoba'))
        ret.append(self.charge_self(1))
        return ret


class Pyronado(ElementalBurstBase):
    name: Literal['Pyronado'] = 'Pyronado'
    desc: str = '''Deals 3 Pyro DMG, creates 1 Pyronado.'''
    damage: int = 3
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 4,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        return super().get_actions(match) + [
            self.create_team_status('Pyronado')
        ]


# Talents


class Crossfire(Crossfire_3_3):
    version: Literal['4.2'] = '4.2'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 3
    )


# charactor base


class Xiangling(CharactorBase):
    name: Literal['Xiangling']
    version: Literal['3.8'] = '3.8'
    desc: str = '''"Exquisite Delicacy" Xiangling'''
    element: ElementType = ElementType.PYRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        DoughFu | GuobaAttack | Pyronado
    ] = []
    faction: List[FactionType] = [
        FactionType.LIYUE
    ]
    weapon_type: WeaponType = WeaponType.POLEARM
    talent: Crossfire | None = None

    def _init_skills(self) -> None:
        self.skills = [
            DoughFu(),
            GuobaAttack(),
            Pyronado(),
        ]
