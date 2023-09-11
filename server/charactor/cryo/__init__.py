from .kaeya import Kaeya, ColdBloodedStrike
from .shenhe import Shenhe, MysticalAbandon, TalismanSpirit
from .eula import Eula, LightfallSword, WellspringOfWarLust
from .chongyun import Chongyun, SteadyBreathing
from .ganyu import Ganyu, SacredCryoPearl, UndividedHeart


CryoCharactors = Kaeya | Shenhe | Eula | Chongyun | Ganyu
SummonsOfCryoCharactors = (
    TalismanSpirit | TalismanSpirit | LightfallSword | SacredCryoPearl
)
CryoCharactorTalents = (
    ColdBloodedStrike | MysticalAbandon | WellspringOfWarLust | SteadyBreathing
    | UndividedHeart
)
