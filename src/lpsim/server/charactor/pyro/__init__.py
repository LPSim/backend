from .fatui_pyro_agent import FatuiPyroAgent, PaidinFull
from .klee import Klee, PoundingSurprise
from .bennett import Bennett, GrandExpectation
from .yoimiya import Yoimiya, NaganoharaMeteorSwarm
from .xiangling import Xiangling, Guoba, Crossfire
from .yanfei import Yanfei, RightOfFinalInterpretation
from .hu_tao import HuTao, SanguineRouge
from .diluc import Diluc, FlowingFlame
from .amber import Amber, BaronBunny, BunnyTriggered
from .abyss_lector_fathomless_flames import (
    AbyssLectorFathomlessFlames, DarkfireFurnace, EmbersRekindled
)
from .dehya import Dehya, FierySanctumField, StalwartAndTrue


PyroCharactors = (
    Diluc | Xiangling | Bennett | Amber | Yoimiya | Klee | HuTao | Yanfei
    | Dehya
    # finally monsters
    | FatuiPyroAgent | AbyssLectorFathomlessFlames
)
SummonsOfPyroCharactors = (
    Guoba | BaronBunny | FierySanctumField
    # finally monsters
    | DarkfireFurnace
)
PyroCharactorTalents = (
    FlowingFlame | Crossfire | GrandExpectation | BunnyTriggered 
    | NaganoharaMeteorSwarm | PoundingSurprise | SanguineRouge 
    | RightOfFinalInterpretation | StalwartAndTrue
    # finally monsters
    | PaidinFull | EmbersRekindled
)
