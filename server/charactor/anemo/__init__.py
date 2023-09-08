from .venti import Venti, Stormeye, EmbraceOfWinds
from .maguu_kenki import (
    MaguuKenki, TranscendentAutomaton, 
    ShadowswordGallopingFrost, ShadowswordLoneGale
)
from .kaedehara_kazuha import (
    KaedeharaKazuha, PoeticsOfFuubutsu, AutumnWhirlwind
)


AnemoCharactors = Venti | MaguuKenki | KaedeharaKazuha
SummonsOfAnemoCharactors = (
    Stormeye | ShadowswordGallopingFrost | ShadowswordLoneGale 
    | AutumnWhirlwind
)
AnemoCharactorTalents = (
    EmbraceOfWinds | TranscendentAutomaton | PoeticsOfFuubutsu
)
