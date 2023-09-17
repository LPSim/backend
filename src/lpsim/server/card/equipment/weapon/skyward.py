from typing import Any, Literal

from ....consts import ObjectPositionType, SkillType, WeaponType
from ....modifiable_values import DamageIncreaseValue
from ....struct import Cost
from .base import RoundEffectWeaponBase


class SkywardBase(RoundEffectWeaponBase):
    name: str
    desc: str = (
        "The character deals +1 DMG. Once per Round: This character's Normal "
        "Attack deal +1 additional DMG."
    )
    cost: Cost = Cost(same_dice_number = 3)
    version: str
    weapon_type: WeaponType
    max_usage_per_round: int = 1

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any, 
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        if self.position.area != ObjectPositionType.CHARACTOR:
            # not equipped
            return value
        super().value_modifier_DAMAGE_INCREASE(value, match, mode)
        if value.is_corresponding_charactor_use_damage_skill(
            self.position, match, SkillType.NORMAL_ATTACK
        ) and self.usage > 0:
            # have usage and is normal attack
            assert mode == 'REAL'
            self.usage -= 1
            value.damage += 1
        return value


class SkywardAtlas(SkywardBase):
    name: Literal['Skyward Atlas']
    version: Literal['3.3'] = '3.3'
    weapon_type: Literal[WeaponType.CATALYST] = WeaponType.CATALYST


class SkywardHarp(SkywardBase):
    name: Literal['Skyward Harp']
    version: Literal['3.3'] = '3.3'
    weapon_type: Literal[WeaponType.BOW] = WeaponType.BOW


class SkywardSpine(SkywardBase):
    name: Literal['Skyward Spine']
    version: Literal['3.3'] = '3.3'
    weapon_type: Literal[WeaponType.POLEARM] = WeaponType.POLEARM


class SkywardBlade(SkywardBase):
    name: Literal['Skyward Blade']
    version: Literal['3.7'] = '3.7'
    weapon_type: Literal[WeaponType.SWORD] = WeaponType.SWORD


class SkywardPride(SkywardBase):
    name: Literal['Skyward Pride']
    version: Literal['3.7'] = '3.7'
    weapon_type: Literal[WeaponType.CLAYMORE] = WeaponType.CLAYMORE


SkywardWeapons = (
    SkywardAtlas | SkywardHarp | SkywardPride | SkywardSpine | SkywardBlade
)
