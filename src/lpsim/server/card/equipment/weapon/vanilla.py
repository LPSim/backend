from typing import Literal

from .....utils.class_registry import register_class

from ....consts import WeaponType
from .base import WeaponBase
from ....struct import Cost


class VanillaWeapon_3_3(WeaponBase):
    name: Literal[
        'Magic Guide',
        'Raven Bow',
        "Traveler's Handy Sword",
        'White Iron Greatsword',
        'White Tassel'
    ]
    version: Literal['3.3'] = '3.3'
    weapon_type: WeaponType = WeaponType.OTHER

    cost: Cost = Cost(same_dice_number = 2)

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        if self.name == 'Magic Guide':
            self.weapon_type = WeaponType.CATALYST
        elif self.name == 'Raven Bow':
            self.weapon_type = WeaponType.BOW
        elif self.name == "Traveler's Handy Sword":
            self.weapon_type = WeaponType.SWORD
        elif self.name == 'White Iron Greatsword':
            self.weapon_type = WeaponType.CLAYMORE
        else:
            assert self.name == 'White Tassel'
            self.weapon_type = WeaponType.POLEARM


register_class(VanillaWeapon_3_3)
