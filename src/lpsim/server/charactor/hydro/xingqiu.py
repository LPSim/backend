from typing import Any, List, Literal

from ...action import Actions

from ...struct import Cost

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Skills


class GuhuaStyle(PhysicalNormalAttackBase):
    name: Literal['Guhua Style'] = 'Guhua Style'
    cost: Cost = PhysicalNormalAttackBase.get_cost(ElementType.HYDRO)


class FatalRainscreen(ElementalSkillBase):
    name: Literal['Fatal Rainscreen'] = 'Fatal Rainscreen'
    desc: str = (
        'Deals 2 Hydro DMG, grants this character Hydro Application, '
        'creates 1 Rain Sword.'
    )
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack, application and create object
        """
        ret = super().get_actions(match)
        ret += [
            self.element_application_self(match, DamageElementalType.HYDRO)
        ]
        if self.is_talent_equipped(match):
            ret += [self.create_team_status('Rain Sword', {
                'usage': 3,
                'max_usage': 3
            })]
        else:
            ret += [self.create_team_status('Rain Sword')]
        return ret


class Raincutter(ElementalBurstBase):
    name: Literal['Raincutter'] = 'Raincutter'
    desc: str = (
        'Deals 1 Hydro DMG, grants this character Hydro Application, creates '
        '1 Rainbow Bladework.'
    )
    damage: int = 1
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack, application and create object
        """
        ret = super().get_actions(match)
        ret += [
            self.element_application_self(match, DamageElementalType.HYDRO)
        ]
        return ret + [
            self.create_team_status('Rainbow Bladework')
        ]


# Talents


class TheScentRemained(SkillTalent):
    name: Literal['The Scent Remained']
    desc: str = (
        'Combat Action: When your active character is Xingqiu, '
        'equip this card. After Xingqiu equips this card, immediately use '
        'Fatal Rainscreen once. When your Xingqiu, who has this card '
        'equipped, creates a Rain Sword, its starting Usage(s)+1.'
    )
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Xingqiu'] = 'Xingqiu'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 4
    )
    skill: FatalRainscreen = FatalRainscreen()


# charactor base


class Xingqiu(CharactorBase):
    name: Literal['Xingqiu']
    version: Literal['3.6'] = '3.6'
    desc: str = '''"Juvenile Galant" Xingqiu'''
    element: ElementType = ElementType.HYDRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[GuhuaStyle | FatalRainscreen | Raincutter] = []
    faction: List[FactionType] = [
        FactionType.LIYUE
    ]
    weapon_type: WeaponType = WeaponType.SWORD
    talent: TheScentRemained | None = None

    def _init_skills(self) -> None:
        self.skills = [
            GuhuaStyle(),
            FatalRainscreen(),
            Raincutter(),
        ]
