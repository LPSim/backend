from .kaeya import Kaeya, ColdBloodedStrike
from .shenhe import Shenhe, MysticalAbandon, TalismanSpirit
from .eula import Eula, LightfallSword, WellspringOfWarLust
from .chongyun import Chongyun, SteadyBreathing
from .ganyu import Ganyu, SacredCryoPearl, UndividedHeart
from .qiqi import Qiqi, RiteOfResurrection, HeraldOfFrost


CryoCharactors = Kaeya | Shenhe | Eula | Chongyun | Ganyu | Qiqi
SummonsOfCryoCharactors = (
    TalismanSpirit | TalismanSpirit | LightfallSword | SacredCryoPearl
    | HeraldOfFrost
)
CryoCharactorTalents = (
    ColdBloodedStrike | MysticalAbandon | WellspringOfWarLust | SteadyBreathing
    | UndividedHeart | RiteOfResurrection
)
