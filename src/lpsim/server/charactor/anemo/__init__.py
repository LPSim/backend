from .venti import Venti, Stormeye, EmbraceOfWinds
from .maguu_kenki import (
    MaguuKenki, TranscendentAutomaton, 
    ShadowswordGallopingFrost, ShadowswordLoneGale
)
from .kaedehara_kazuha import (
    KaedeharaKazuha, PoeticsOfFuubutsu, AutumnWhirlwind
)


AnemoCharactors = (
    Venti | KaedeharaKazuha 
    # finally monsters
    | MaguuKenki
)
SummonsOfAnemoCharactors = (
    Stormeye | AutumnWhirlwind
    # finally monsters
    | ShadowswordGallopingFrost | ShadowswordLoneGale 
)
AnemoCharactorTalents = (
    EmbraceOfWinds | PoeticsOfFuubutsu
    # finally monsters
    | TranscendentAutomaton
)
