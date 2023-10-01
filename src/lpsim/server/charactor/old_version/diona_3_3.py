from typing import Literal

from ...struct import Cost

from ...consts import DieColor
from ..cryo.diona import ShakenNotPurred as SNP_4_1


class ShakenNotPurred_3_3(SNP_4_1):
    version: Literal['3.3']
    cost: Cost = Cost(
        elemental_dice_color = DieColor.CRYO,
        elemental_dice_number = 4
    )
