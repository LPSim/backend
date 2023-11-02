from .nahida import Nahida, TheSeedOfStoredKnowledge
from .collei import Collei, FloralSidewinder, CuileinAnbar
from .tighnari import Tighnari, KeenSight, ClusterbloomArrow
from .jadeplume_terrorshroom import JadeplumeTerrorshroom, ProliferatingSpores
from .yaoyao import Yaoyao, YueguiThrowingMode, Beneficent
from .baizhu import Baizhu, AllThingsAreOfTheEarth, GossamerSprite


DendroCharactors = (
    Collei | Tighnari | Nahida | Yaoyao | Baizhu
    # finally monsters
    | JadeplumeTerrorshroom
)
SummonsOfDendroCharactors = (
    CuileinAnbar | ClusterbloomArrow | YueguiThrowingMode | GossamerSprite
)
DendroCharactorTalents = (
    FloralSidewinder | KeenSight | TheSeedOfStoredKnowledge | Beneficent
    | AllThingsAreOfTheEarth
    # finally monsters
    | ProliferatingSpores
)
