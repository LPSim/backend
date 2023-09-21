from .venti import Venti, Stormeye, EmbraceOfWinds
from .maguu_kenki import (
    MaguuKenki, TranscendentAutomaton, 
    ShadowswordGallopingFrost, ShadowswordLoneGale
)
from .kaedehara_kazuha import (
    KaedeharaKazuha, PoeticsOfFuubutsu, AutumnWhirlwind
)
from .sucrose import Sucrose, LargeWindSpirit, ChaoticEntropy


AnemoCharactors = (
    Sucrose | Venti | KaedeharaKazuha 
    # finally monsters
    | MaguuKenki
)
SummonsOfAnemoCharactors = (
    LargeWindSpirit | Stormeye | AutumnWhirlwind
    # finally monsters
    | ShadowswordGallopingFrost | ShadowswordLoneGale 
)
AnemoCharactorTalents = (
    ChaoticEntropy | EmbraceOfWinds | PoeticsOfFuubutsu
    # finally monsters
    | TranscendentAutomaton
)
