from .fatui_pyro_agent import FatuiPyroAgent, PaidinFull
from .klee import Klee, PoundingSurprise


PyroCharactors = FatuiPyroAgent | Klee
# SummonsOfPyroCharactors = 
PyroCharactorTalents = PaidinFull | PoundingSurprise
