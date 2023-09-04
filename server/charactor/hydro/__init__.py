from .mona import Mona, ProphecyOfSubmersion, Reflection
from .barbara import Barbara, MelodyLoop, GloriousSeason
from .rhodeia import RhodeiaOfLoch, StreamingSurge, Frog, Squirrel, Raptor


HydroCharactors = Mona | Barbara | RhodeiaOfLoch
SummonsOfHydroCharactors = Reflection | MelodyLoop | Frog | Squirrel | Raptor
HydroCharactorTalents = ProphecyOfSubmersion | GloriousSeason | StreamingSurge
