from typing import Any, List, Literal

from ...action import Actions, CreateObjectAction, RemoveObjectAction
from ...struct import Cost

from ...consts import (
    ELEMENT_TO_DAMAGE_TYPE, DamageElementalType, DieColor, ElementType, 
    FactionType, ObjectPositionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalNormalAttackBase, ElementalSkillBase, 
    CharactorBase, SkillTalent
)


# Skills


class InfluxBlast(ElementalSkillBase):
    name: Literal['Influx Blast'] = 'Influx Blast'
    desc: str = (
        'Deals 2 Hydro DMG. The target character receives Refraction.'
    )
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
        target_charactor = match.player_tables[
            1 - self.position.player_idx].get_active_charactor()
        args = {}
        if self.is_talent_equipped(match):
            args = {
                'usage': 3,
                'max_usage': 3,
                'is_talent_activated': True,
            }
        return super().get_actions(match) + ret + [
            CreateObjectAction(
                object_position = target_charactor.position.set_area(
                    ObjectPositionType.CHARACTOR_STATUS
                ),
                object_name = 'Refraction',
                object_arguments = args
            )
        ]


# Talents


class MirrorCage(SkillTalent):
    name: Literal['Mirror Cage']
    desc: str = (
        'Combat Action: When your active character is Mirror Maiden, equip '
        'this card. After Mirror Maiden equips this card, immediately use '
        'Influx Blast once. When your Mirror Maiden, who has this card '
        'equipped, creates a Refraction, it will have the following effects: '
        'Starting Duration (Rounds) +1, will increase the Elemental Dice Cost '
        'of switching from a character to which this is attached to another '
        'character by 1.'
    )
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Mirror Maiden'] = 'Mirror Maiden'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 4
    )
    skill: InfluxBlast = InfluxBlast()

# charactor base


class MirrorMaiden(CharactorBase):
    name: Literal['Mirror Maiden']
    version: Literal['3.7'] = '3.7'
    desc: str = '''"Snezhnayan Maiden" Mirror Envoy'''
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
    talent: MirrorCage | None = None

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
