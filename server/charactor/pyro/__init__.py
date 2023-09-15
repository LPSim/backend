from .fatui_pyro_agent import FatuiPyroAgent, PaidinFull
from .klee import Klee, PoundingSurprise
from .bennett import Bennett, GrandExpectation
from .yoimiya import Yoimiya, NaganoharaMeteorSwarm
from .xiangling import Xiangling, Guoba, Crossfire
from .yanfei import Yanfei, RightOfFinalInterpretation
from .hu_tao import HuTao, SanguineRouge
from .diluc import Diluc, FlowingFlame


PyroCharactors = (
    Diluc | Xiangling | Bennett | Yoimiya | Klee | HuTao | Yanfei
    # finally monsters
    | FatuiPyroAgent
)
SummonsOfPyroCharactors = Guoba | Guoba
PyroCharactorTalents = (
    FlowingFlame | Crossfire | GrandExpectation | NaganoharaMeteorSwarm
    | PoundingSurprise | SanguineRouge | RightOfFinalInterpretation
    # finally monsters
    | PaidinFull
)
