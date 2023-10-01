from .nahida import Nahida, TheSeedOfStoredKnowledge
from .collei import Collei, FloralSidewinder, CuileinAnbar
from .tighnari import Tighnari, KeenSight, ClusterbloomArrow
from .jadeplume_terrorshroom import JadeplumeTerrorshroom, ProliferatingSpores
from .yaoyao import Yaoyao, YueguiThrowingMode, Beneficent


DendroCharactors = (
    Collei | Tighnari | Nahida | Yaoyao
    # finally monsters
    | JadeplumeTerrorshroom
)
SummonsOfDendroCharactors = (
    CuileinAnbar | ClusterbloomArrow | YueguiThrowingMode
)
DendroCharactorTalents = (
    FloralSidewinder | KeenSight | TheSeedOfStoredKnowledge | Beneficent
    # finally monsters
    | ProliferatingSpores
)
