from .fatui_pyro_agent import FatuiPyroAgent, PaidinFull
from .klee import Klee, PoundingSurprise
from .bennett import Bennett, GrandExpectation
from .yoimiya import Yoimiya, NaganoharaMeteorSwarm


PyroCharactors = FatuiPyroAgent | Klee | Bennett | Yoimiya
# SummonsOfPyroCharactors = 
PyroCharactorTalents = (
    PaidinFull | PoundingSurprise | GrandExpectation | NaganoharaMeteorSwarm
)
