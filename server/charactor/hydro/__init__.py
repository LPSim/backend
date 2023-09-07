from .mona import Mona, ProphecyOfSubmersion, Reflection
from .barbara import Barbara, MelodyLoop, GloriousSeason
from .rhodeia import RhodeiaOfLoch, StreamingSurge, Frog, Squirrel, Raptor
from .xingqiu import Xingqiu, TheScentRemained


HydroCharactors = Mona | Barbara | RhodeiaOfLoch | Xingqiu
SummonsOfHydroCharactors = Reflection | MelodyLoop | Frog | Squirrel | Raptor
HydroCharactorTalents = (
    ProphecyOfSubmersion | GloriousSeason | StreamingSurge | TheScentRemained
)
