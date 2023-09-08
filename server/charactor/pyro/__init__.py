from .fatui_pyro_agent import FatuiPyroAgent, PaidinFull
from .klee import Klee, PoundingSurprise
from .bennett import Bennett, GrandExpectation
from .yoimiya import Yoimiya, NaganoharaMeteorSwarm
from .xiangling import Xiangling, Guoba, Crossfire


PyroCharactors = FatuiPyroAgent | Klee | Bennett | Yoimiya | Xiangling
SummonsOfPyroCharactors = Guoba | Guoba
PyroCharactorTalents = (
    PaidinFull | PoundingSurprise | GrandExpectation | NaganoharaMeteorSwarm
    | Crossfire
)
