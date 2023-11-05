from .mona import Mona, ProphecyOfSubmersion, Reflection
from .barbara import Barbara, MelodyLoop, GloriousSeason
from .rhodeia import RhodeiaOfLoch
from .xingqiu import Xingqiu, TheScentRemained
from .tartaglia import Tartaglia, AbyssalMayhemHydrospout
from .sangonomiya_kokomi import (
    SangonomiyaKokomi, BakeKurage, TamakushiCasket
)
from .candace import Candace, TheOverflow
from .mirror_maiden import MirrorMaiden, MirrorCage
from .kamisato_ayato import KamisatoAyato, GardenOfPurity, KyoukaFuushi
from .nilou import Nilou, TheStarrySkiesTheirFlowersRain, BounatifulCore


HydroCharactors = (
    Barbara | Xingqiu | Mona | Tartaglia | SangonomiyaKokomi | KamisatoAyato 
    | Candace | Nilou
    # finally monsters
    | RhodeiaOfLoch | MirrorMaiden
)
SummonsOfHydroCharactors = (
    MelodyLoop | Reflection | BakeKurage | GardenOfPurity | BounatifulCore
    # finally monsters
)
HydroCharactorTalents = (
    GloriousSeason | TheScentRemained | ProphecyOfSubmersion
    | AbyssalMayhemHydrospout | TamakushiCasket | KyoukaFuushi | TheOverflow
    | TheStarrySkiesTheirFlowersRain
    # finally monsters
    | MirrorCage
)
