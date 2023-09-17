from .nahida import Nahida, TheSeedOfStoredKnowledge
from .collei import Collei, FloralSidewinder, CuileinAnbar
from .tighnari import Tighnari, KeenSight, ClusterbloomArrow


DendroCharactors = Collei | Tighnari | Nahida
SummonsOfDendroCharactors = CuileinAnbar | ClusterbloomArrow
DendroCharactorTalents = (
    FloralSidewinder | KeenSight | TheSeedOfStoredKnowledge
)
