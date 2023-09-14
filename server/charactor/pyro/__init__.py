from .fatui_pyro_agent import FatuiPyroAgent, PaidinFull
from .klee import Klee, PoundingSurprise
from .bennett import Bennett, GrandExpectation
from .yoimiya import Yoimiya, NaganoharaMeteorSwarm
from .xiangling import Xiangling, Guoba, Crossfire
from .yanfei import Yanfei, RightOfFinalInterpretation
from .hu_tao import HuTao, SanguineRouge
from .diluc import Diluc, FlowingFlame


PyroCharactors = (
    FatuiPyroAgent | Klee | Bennett | Yoimiya | Xiangling | Yanfei | HuTao
    | Diluc
)
SummonsOfPyroCharactors = Guoba | Guoba
PyroCharactorTalents = (
    PaidinFull | PoundingSurprise | GrandExpectation | NaganoharaMeteorSwarm
    | Crossfire | RightOfFinalInterpretation | SanguineRouge | FlowingFlame
)
