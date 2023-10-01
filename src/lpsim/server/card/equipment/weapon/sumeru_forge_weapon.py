

from typing import Any, List, Literal

from ....action import CreateObjectAction, DrawCardAction

from ....struct import Cost
from .base import WeaponBase
from ....consts import ObjectPositionType, WeaponType


class FruitOfFulfillment(WeaponBase):
    name: Literal['Fruit of Fulfillment']
    desc: str = '''The character deals +1 DMG. When played: Draw 2 cards.'''
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


class KingsSquire(WeaponBase):
    name: Literal["King's Squire"]
    desc: str = (
        'The character deals +1 DMG. When played: The character to which this '
        'is attached will spend 2 less Elemental Dice next time they use an '
        'Elemental Skill or equip a Talent card.'
    )
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


class Moonpiercer(KingsSquire):
    name: Literal['Moonpiercer']
    version: Literal['4.1'] = '4.1'
    weapon_type: WeaponType = WeaponType.POLEARM


SumeruForgeWeapons = FruitOfFulfillment | KingsSquire | Moonpiercer
