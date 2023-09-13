from .nahida import Nahida, TheSeedOfStoredKnowledge
from .collei import Collei, FloralSidewinder, CuileinAnbar
from .tighnari import Tighnari, KeenSight, ClusterbloomArrow


DendroCharactors = Nahida | Collei | Tighnari
SummonsOfDendroCharactors = CuileinAnbar | ClusterbloomArrow
DendroCharactorTalents = (
    TheSeedOfStoredKnowledge | FloralSidewinder | KeenSight
)
