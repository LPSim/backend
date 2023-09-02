from .mona import Mona, ProphecyOfSubmersion, Reflection
from .barbara import Barbara, MelodyLoop, GloriousSeason


HydroCharactors = Mona | Barbara
SummonsOfHydroCharactors = Reflection | MelodyLoop
HydroCharactorTalents = ProphecyOfSubmersion | GloriousSeason
