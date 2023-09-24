from .mona import Mona, ProphecyOfSubmersion, Reflection
from .barbara import Barbara, MelodyLoop, GloriousSeason
from .rhodeia import RhodeiaOfLoch, StreamingSurge, Frog, Squirrel, Raptor
from .xingqiu import Xingqiu, TheScentRemained
from .tartaglia import Tartaglia, AbyssalMayhemHydrospout
from .sangonomiya_kokomi import (
    SangonomiyaKokomi, BakeKurage, TamakushiCasket
)
from .candace import Candace, TheOverflow
from .mirror_maiden import MirrorMaiden, MirrorCage


HydroCharactors = (
    Barbara | Xingqiu | Mona | Tartaglia | SangonomiyaKokomi | Candace
    # finally monsters
    | RhodeiaOfLoch | MirrorMaiden
)
SummonsOfHydroCharactors = (
    MelodyLoop | Reflection | BakeKurage 
    # finally monsters
    | Frog | Squirrel | Raptor
)
HydroCharactorTalents = (
    GloriousSeason | TheScentRemained | ProphecyOfSubmersion
    | AbyssalMayhemHydrospout | TamakushiCasket | TheOverflow
    # finally monsters
    | StreamingSurge | MirrorCage
)
