from .fatui_pyro_agent import FatuiPyroAgent, PaidinFull
from .klee import Klee, PoundingSurprise
from .bennett import Bennett, GrandExpectation
from .yoimiya import Yoimiya, NaganoharaMeteorSwarm
from .xiangling import Xiangling, Guoba, Crossfire
from .yanfei import Yanfei, RightOfFinalInterpretation


PyroCharactors = FatuiPyroAgent | Klee | Bennett | Yoimiya | Xiangling | Yanfei
SummonsOfPyroCharactors = Guoba | Guoba
PyroCharactorTalents = (
    PaidinFull | PoundingSurprise | GrandExpectation | NaganoharaMeteorSwarm
    | Crossfire | RightOfFinalInterpretation
)
