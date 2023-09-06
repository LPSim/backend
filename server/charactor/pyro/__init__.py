from .fatui_pyro_agent import FatuiPyroAgent, PaidinFull
from .klee import Klee, PoundingSurprise
from .bennett import Bennett, GrandExpectation


PyroCharactors = FatuiPyroAgent | Klee | Bennett
# SummonsOfPyroCharactors = 
PyroCharactorTalents = PaidinFull | PoundingSurprise | GrandExpectation
