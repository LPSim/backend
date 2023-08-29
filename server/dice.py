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
    position: ObjectPosition = ObjectPosition(
        player_id = -1,
        area = ObjectPositionType.INVALID
    )
    type: Literal[ObjectType.DICE] = ObjectType.DICE
    colors: list[DieColor] = []

    def colors_to_idx(self, colors: List[DieColor]) -> List[int]:
        """
        Convert colors to idx.
        """
        res: List[int] = []
        selected = [DieColor[x.upper()] for x in colors]
        all_c: List[DieColor | None] = list(self.colors)
        for x in selected:
            res.append(all_c.index(x))
            all_c[all_c.index(x)] = None
        return res
