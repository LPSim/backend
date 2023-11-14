

from typing import Any, List, Literal

from .....utils.class_registry import register_class

from ....action import CreateObjectAction, DrawCardAction

from ....struct import Cost
from .base import WeaponBase
from ....consts import ObjectPositionType, WeaponType


class FruitOfFulfillment_3_8(WeaponBase):
    name: Literal['Fruit of Fulfillment']
    cost: Cost = Cost(any_dice_number = 3)
    version: Literal['3.8'] = '3.8'
    weapon_type: WeaponType = WeaponType.CATALYST

    def equip(self, match: Any) -> List[DrawCardAction]:
        """
        draw 2 cards
        """
        return [DrawCardAction(
            player_idx = self.position.player_idx,
            number = 2,
            draw_if_filtered_not_enough = True
        )]


class KingsSquire_4_0(WeaponBase):
    name: Literal["King's Squire"]
    cost: Cost = Cost(same_dice_number = 3)
    version: Literal['4.0'] = '4.0'
    weapon_type: WeaponType = WeaponType.BOW

    def equip(self, match: Any) -> List[CreateObjectAction]:
        """
        attach status
        """
        return [CreateObjectAction(
            object_position = self.position.set_area(
                ObjectPositionType.CHARACTOR_STATUS),
            object_name = self.name,
            object_arguments = {}
        )]


class Moonpiercer_4_1(KingsSquire_4_0):
    name: Literal['Moonpiercer']
    version: Literal['4.1'] = '4.1'
    weapon_type: WeaponType = WeaponType.POLEARM


register_class(FruitOfFulfillment_3_8 | KingsSquire_4_0 | Moonpiercer_4_1)
