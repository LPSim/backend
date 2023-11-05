"""
Old version of charactors, summons and talents. Status are not defined here,
and old status will be implemented in their old_version.py.

For versions before 3.7, it will have one file for each charactor, and they
will related on new charactors. For versions after 3.8, newest version of
charactors will related on old charactors.
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
from .xingqiu_4_1 import Xingqiu_4_1, TheScentRemained_3_3
from .arataki_itto_3_6 import AratakiItto_3_6, AratakiIchiban_3_6, Ushi_3_6
from .jean_3_3 import Jean_3_3, DandelionField_3_3, LandsOfDandelion_3_3
from .rhodeia_3_3 import (
    RhodeiaOfLoch_3_3, Frog_3_3, Squirrel_3_3, Raptor_3_3, StreamingSurge_3_3
)
from .shenhe_3_7 import Shenhe_3_7, TalismanSpirit_3_7, MysticalAbandon_3_7
from .yanfei_3_8 import Yanfei_3_8, RightOfFinalInterpretation_3_8
from .talent_cards_4_2 import (
    MirrorCage_3_3, GloriousSeason_3_3, AbsorbingPrism_3_7, Crossfire_3_3,
    TheOverflow_3_8, SteadyBreathing_3_3, NaganoharaMeteorSwarm_3_3, 
    Awakening_3_3, LightningStorm_3_4, SinOfPride_3_5, TamakushiCasket_3_5,
    BunnyTriggered_3_7, FeatherfallJudgment_3_3
)


OldTalents = (
    RightOfFinalInterpretation_3_8 | TheOverflow_3_8

    | AbyssalMayhemHydrospout_3_7 | MysticalAbandon_3_7 | AbsorbingPrism_3_7
    | BunnyTriggered_3_7

    | AratakiIchiban_3_6

    | TamakushiCasket_3_5 | SinOfPride_3_5 
    
    | LightningStorm_3_4

    | FloralSidewinder_3_3 | UndividedHeart_3_3 | ShakenNotPurred_3_3
    | TheScentRemained_3_3 | LandsOfDandelion_3_3 | StreamingSurge_3_3
    | MirrorCage_3_3 | GloriousSeason_3_3 | Crossfire_3_3 | SteadyBreathing_3_3
    | NaganoharaMeteorSwarm_3_3 | Awakening_3_3 | FeatherfallJudgment_3_3
)
OldSummons = (
    CryoCicins_3_7 | TalismanSpirit_3_7

    | Ushi_3_6

    | LightfallSword_3_5

    | Frog_3_3 | Squirrel_3_3 | Raptor_3_3 | DandelionField_3_3
)
OldCharactors = (
    Xingqiu_4_1

    | Yanfei_3_8

    | Tartaglia_3_7 | FatuiCryoCicinMage_3_7 | Shenhe_3_7

    | Xingqiu_3_6 | KamisatoAyato_3_6 | AratakiItto_3_6

    | Eula_3_5 | SangonomiyaKokomi_3_5 

    | Yoimiya_3_4 | Beidou_3_4

    | MaguuKenki_3_3 | Yoimiya_3_3 | Xingqiu_3_3 | Xiangling_3_3 | Ganyu_3_3
    | Razor_3_3 | MirrorMaiden_3_3 | RhodeiaOfLoch_3_3 | Jean_3_3
)
