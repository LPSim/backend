from typing import List, Literal

from .struct import ObjectPosition
from .consts import DieColor, ObjectPositionType
from .object_base import ObjectBase, ObjectType


class Dice(ObjectBase):
    """
    Class representing dice.

    Attributes:
        colors: list of colors of dice.
    """
    name: Literal['Dice'] = 'Dice'
    position: ObjectPosition = ObjectPosition(
        player_idx = -1,
        area = ObjectPositionType.INVALID,
        id = -1,
    )
    type: Literal[ObjectType.DICE] = ObjectType.DICE
    colors: List[DieColor] = []

    def colors_to_idx(self, colors: List[DieColor]) -> List[int]:
        """
        Convert colors to idx.
        """
        res: List[int] = []
        all_c: List[DieColor | None] = list(self.colors)
        for x in colors:
            res.append(all_c.index(x))
            all_c[all_c.index(x)] = None
        return res
