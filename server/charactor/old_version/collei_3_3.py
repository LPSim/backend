from typing import Literal

from ...consts import DieColor
from ...struct import Cost
from ..dendro.collei import FloralSidewinder as FloralSidewinder_3_4


class FloralSidewinder_3_3(FloralSidewinder_3_4):
    version: Literal['3.3']
    cost: Cost = Cost(
        elemental_dice_color = DieColor.DENDRO,
        elemental_dice_number = 3
    )
