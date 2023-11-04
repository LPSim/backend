from typing import Literal

from ...struct import Cost
from ...consts import DieColor
from ..old_version.xingqiu_4_1 import Xingqiu_4_1 as X_4_1
from ..old_version.xingqiu_4_1 import TheScentRemained_3_3 as TSR_4_1
from ..old_version.xingqiu_4_1 import FatalRainscreen


class TheScentRemained(TSR_4_1):
    name: Literal['The Scent Remained']
    desc: str = (
        'Combat Action: When your active character is Xingqiu, '
        'equip this card. After Xingqiu equips this card, immediately use '
        'Fatal Rainscreen once. When your Xingqiu, who has this card '
        'equipped, creates a Rain Sword, its starting Usage(s)+1, and '
        'can block DMG of at least 2 for your active charactor.'
    )
    version: Literal['4.2'] = '4.2'
    charactor_name: Literal['Xingqiu'] = 'Xingqiu'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.HYDRO,
        elemental_dice_number = 3
    )
    skill: Literal['Fatal Rainscreen'] = 'Fatal Rainscreen'


class Xingqiu(X_4_1):
    version: Literal['4.2']

    talent: TheScentRemained | None = None
