"""
Old version of charactors, summons and talents. Status are not defined here,
and old status will be implemented in their old_version.py.
"""
from .eula_3_5 import Eula_3_5, LightfallSword_3_5
from .sangonomiya_kokomi_3_5 import SangonomiyaKokomi_3_5
from .yoimiya_3_4 import Yoimiya_3_4
from .collei_3_3 import FloralSidewinder_3_3
from .maguu_kenki_3_3 import MaguuKenki_3_3
from .yoimiya_3_3 import Yoimiya_3_3
from .xingqiu_3_3 import Xingqiu_3_3
from .xiangling_3_3 import Xiangling_3_3
from .ganyu_3_3 import Ganyu_3_3, UndividedHeart_3_3


OldTalents = FloralSidewinder_3_3 | FloralSidewinder_3_3 | UndividedHeart_3_3
OldSummons = LightfallSword_3_5 | LightfallSword_3_5
OldCharactors = (
    Eula_3_5 | SangonomiyaKokomi_3_5 

    | Yoimiya_3_4 

    | MaguuKenki_3_3 | Yoimiya_3_3 | Xingqiu_3_3 | Xiangling_3_3 | Ganyu_3_3
)
