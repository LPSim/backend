from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...action import Actions, RemoveObjectAction
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


class InfluxBlast(ElementalSkillBase):
    name: Literal['Influx Blast'] = 'Influx Blast'
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.HYDRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        First remove existing Refraction on opposite, then create new
        Refraction.
        """
        target_charactors = match.player_tables[
            1 - self.position.player_idx].charactors
        exist_status = None
        for charactor in target_charactors:
            for status in charactor.status:
                if status.name == 'Refraction':
                    exist_status = status
                    break
            if exist_status is not None:
                break
        ret: List[Actions] = []
        if exist_status:
            ret.append(RemoveObjectAction(
                object_position = exist_status.position
            ))
        args = {}
        if self.is_talent_equipped(match):
            args = {
                'usage': 3,
                'max_usage': 3,
                'is_talent_activated': True,
            }
        return super().get_actions(match) + ret + [
            self.create_opposite_charactor_status(
                match, 'Refraction', args
            )
        ]


# Talents


class MirrorCage_3_3(SkillTalent):
    name: Literal['Mirror Cage']
    version: Literal['3.3']
    charactor_name: Literal['Mirror Maiden'] = 'Mirror Maiden'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 4
    )
    skill: Literal['Influx Blast'] = 'Influx Blast'


class MirrorCage_4_2(MirrorCage_3_3):
    version: Literal['4.2'] = '4.2'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3,
    )


# charactor base


class MirrorMaiden_3_7(CharactorBase):
    name: Literal['Mirror Maiden']
    version: Literal['3.7'] = '3.7'
    element: ElementType = ElementType.HYDRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        ElementalNormalAttackBase | InfluxBlast | ElementalBurstBase
    ] = []
    faction: List[FactionType] = [
        FactionType.FATUI
    ]
    weapon_type: WeaponType = WeaponType.OTHER

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name = 'Water Ball',
                damage_type = ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost = ElementalNormalAttackBase.get_cost(self.element),
            ),
            InfluxBlast(),
            ElementalBurstBase(
                name = 'Rippled Reflection',
                damage = 5,
                damage_type = ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost = ElementalBurstBase.get_cost(self.element, 3, 2)
            )
        ]


register_class(MirrorMaiden_3_7 | MirrorCage_4_2 | MirrorCage_3_3)
