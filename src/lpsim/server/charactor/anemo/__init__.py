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


AnemoCharactors = (
    Sucrose | Jean | Venti | KaedeharaKazuha 
    # finally monsters
    | MaguuKenki
)
SummonsOfAnemoCharactors = (
    LargeWindSpirit | DandelionField | Stormeye | AutumnWhirlwind
    # finally monsters
    | ShadowswordGallopingFrost | ShadowswordLoneGale 
)
AnemoCharactorTalents = (
    ChaoticEntropy | LandsOfDandelion | EmbraceOfWinds | PoeticsOfFuubutsu
    # finally monsters
    | TranscendentAutomaton
)
