from .venti import Venti, Stormeye, EmbraceOfWinds
from .maguu_kenki import (
    MaguuKenki, TranscendentAutomaton, 
    ShadowswordGallopingFrost, ShadowswordLoneGale
)


AnemoCharactors = Venti | MaguuKenki
SummonsOfAnemoCharactors = (
    Stormeye | ShadowswordGallopingFrost | ShadowswordLoneGale
)
AnemoCharactorTalents = EmbraceOfWinds | TranscendentAutomaton
