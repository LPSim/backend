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


AnemoCharactors = (
    Sucrose | Jean | Venti | Xiao | KaedeharaKazuha 
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
    | ConquerorOfEvilGuardianYaksha | PoeticsOfFuubutsu
    # finally monsters
    | TranscendentAutomaton
)
