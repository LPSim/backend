from typing import Any, List, Literal

from ....utils.class_registry import register_class

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
        ret = [
            self.attack_opposite_active(match, self.damage, self.damage_type),
            self.charge_self(1),
        ]
        ele_app = self.element_application_self(
            match, DamageElementalType.HYDRO
        )
        ret[0].damage_value_list += ele_app.damage_value_list
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        talent = charactor.talent
        if talent is not None:
            ret += [self.create_team_status('Rain Sword', {
                'version': talent.version,
                'usage': 3,
                'max_usage': 3,
            })]
        else:
            ret += [self.create_team_status('Rain Sword', {
                'version': '3.3'
            })]
        return ret


class Raincutter(ElementalBurstBase):
    name: Literal['Raincutter'] = 'Raincutter'
    damage: int = 2
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
        ret = [
            self.charge_self(-self.cost.charge),
            self.attack_opposite_active(match, self.damage, self.damage_type),
        ]
        ele_app = self.element_application_self(
            match, DamageElementalType.HYDRO
        )
        ret[1].damage_value_list += ele_app.damage_value_list
        return ret + [
            self.create_team_status('Rainbow Bladework')
        ]


# Talents


class TheScentRemained_3_3(SkillTalent):
    name: Literal['The Scent Remained']
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Xingqiu'] = 'Xingqiu'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 4
    )
    skill: Literal['Fatal Rainscreen'] = 'Fatal Rainscreen'


class TheScentRemained_4_2(TheScentRemained_3_3):
    name: Literal['The Scent Remained']
    version: Literal['4.2'] = '4.2'
    charactor_name: Literal['Xingqiu'] = 'Xingqiu'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3
    )
    skill: Literal['Fatal Rainscreen'] = 'Fatal Rainscreen'
# charactor base


class Xingqiu_4_1(CharactorBase):
    name: Literal['Xingqiu']
    version: Literal['4.1'] = '4.1'
    element: ElementType = ElementType.HYDRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[GuhuaStyle | FatalRainscreen | Raincutter] = []
    faction: List[FactionType] = [
        FactionType.LIYUE
    ]
    weapon_type: WeaponType = WeaponType.SWORD

    def _init_skills(self) -> None:
        self.skills = [
            GuhuaStyle(),
            FatalRainscreen(),
            Raincutter(),
        ]


register_class(Xingqiu_4_1 | TheScentRemained_3_3 | TheScentRemained_4_2)
