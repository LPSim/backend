from .venti import Venti, Stormeye, EmbraceOfWinds
from .maguu_kenki import (
    MaguuKenki, TranscendentAutomaton, 
    ShadowswordGallopingFrost, ShadowswordLoneGale
)
from .kaedehara_kazuha import (
    KaedeharaKazuha, PoeticsOfFuubutsu, AutumnWhirlwind
)
from .sucrose import Sucrose, LargeWindSpirit, ChaoticEntropy
from .jean import Jean, DandelionField, LandsOfDandelion
from .xiao import Xiao, ConquerorOfEvilGuardianYaksha
from .wanderer import Wanderer, GalesOfReverie


AnemoCharactors = (
    Sucrose | Jean | Venti | Xiao | KaedeharaKazuha | Wanderer
    # finally monsters
    | MaguuKenki
)
SummonsOfAnemoCharactors = (
    LargeWindSpirit | DandelionField | Stormeye | AutumnWhirlwind
    # finally monsters
    | ShadowswordGallopingFrost | ShadowswordLoneGale 
)
AnemoCharactorTalents = (
    ChaoticEntropy | LandsOfDandelion | EmbraceOfWinds 
    | ConquerorOfEvilGuardianYaksha | PoeticsOfFuubutsu | GalesOfReverie
    # finally monsters
    | TranscendentAutomaton
)
