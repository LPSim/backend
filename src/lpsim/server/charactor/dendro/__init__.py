from .nahida import Nahida, TheSeedOfStoredKnowledge
from .collei import Collei, FloralSidewinder, CuileinAnbar
from .tighnari import Tighnari, KeenSight, ClusterbloomArrow
from .jadeplume_terrorshroom import JadeplumeTerrorshroom, ProliferatingSpores


DendroCharactors = (
    Collei | Tighnari | Nahida 
    # finally monsters
    | JadeplumeTerrorshroom
)
SummonsOfDendroCharactors = CuileinAnbar | ClusterbloomArrow
DendroCharactorTalents = (
    FloralSidewinder | KeenSight | TheSeedOfStoredKnowledge
    # finally monsters
    | ProliferatingSpores
)
