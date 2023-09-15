
from typing import Any, List, Literal

from ....action import CreateObjectAction

from ....consts import ObjectPositionType, WeaponType

from ....struct import Cost
from .base import WeaponBase


class KingsSquire(WeaponBase):
    name: Literal["King's Squire"] = "King's Squire"
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


Bows = KingsSquire | KingsSquire
