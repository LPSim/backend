"""
Old version of charactors, summons and talents. Status are not defined here,
and old status will be implemented in their old_version.py.
"""
from .beidou_3_4 import Beidou_3_4
from .razor_3_3 import Razor_3_3
from .eula_3_5 import Eula_3_5, LightfallSword_3_5
from .sangonomiya_kokomi_3_5 import SangonomiyaKokomi_3_5
from .yoimiya_3_4 import Yoimiya_3_4
from .collei_3_3 import FloralSidewinder_3_3
from .maguu_kenki_3_3 import MaguuKenki_3_3
from .yoimiya_3_3 import Yoimiya_3_3
from .xingqiu_3_3 import Xingqiu_3_3
from .xingqiu_3_6 import Xingqiu_3_6
from .xiangling_3_3 import Xiangling_3_3
from .ganyu_3_3 import Ganyu_3_3, UndividedHeart_3_3
from .mirror_maiden_3_3 import MirrorMaiden_3_3
from .fatui_cryo_cicin_mage_3_7 import FatuiCryoCicinMage_3_7, CryoCicins_3_7
from .kamisato_ayato_3_6 import KamisatoAyato_3_6
from .tartaglia_3_7 import Tartaglia_3_7, AbyssalMayhemHydrospout_3_7
from .diona_3_3 import ShakenNotPurred_3_3


OldTalents = (
    AbyssalMayhemHydrospout_3_7

    | FloralSidewinder_3_3 | UndividedHeart_3_3 | ShakenNotPurred_3_3
)
OldSummons = (
    CryoCicins_3_7 

    | LightfallSword_3_5
)
OldCharactors = (
    Tartaglia_3_7 | FatuiCryoCicinMage_3_7

    | Xingqiu_3_6 | KamisatoAyato_3_6

    | Eula_3_5 | SangonomiyaKokomi_3_5 

    | Yoimiya_3_4 | Beidou_3_4

    | MaguuKenki_3_3 | Yoimiya_3_3 | Xingqiu_3_3 | Xiangling_3_3 | Ganyu_3_3
    | Razor_3_3 | MirrorMaiden_3_3
)
