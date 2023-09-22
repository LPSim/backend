from .fatui_pyro_agent import FatuiPyroAgent, PaidinFull
from .klee import Klee, PoundingSurprise
from .bennett import Bennett, GrandExpectation
from .yoimiya import Yoimiya, NaganoharaMeteorSwarm
from .xiangling import Xiangling, Guoba, Crossfire
from .yanfei import Yanfei, RightOfFinalInterpretation
from .hu_tao import HuTao, SanguineRouge
from .diluc import Diluc, FlowingFlame
from .amber import Amber, BaronBunny, BunnyTriggered


PyroCharactors = (
    Diluc | Xiangling | Bennett | Amber | Yoimiya | Klee | HuTao | Yanfei
    # finally monsters
    | FatuiPyroAgent
)
SummonsOfPyroCharactors = Guoba | BaronBunny
PyroCharactorTalents = (
    FlowingFlame | Crossfire | GrandExpectation | BunnyTriggered 
    | NaganoharaMeteorSwarm | PoundingSurprise | SanguineRouge 
    | RightOfFinalInterpretation
    # finally monsters
    | PaidinFull
)
