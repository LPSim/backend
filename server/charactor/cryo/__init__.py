from .kaeya import Kaeya, ColdBloodedStrike
from .shenhe import Shenhe, MysticalAbandon, TalismanSpirit
from .eula import Eula, LightfallSword, WellspringOfWarLust
from .chongyun import Chongyun, SteadyBreathing
from .ganyu import Ganyu, SacredCryoPearl, UndividedHeart
from .qiqi import Qiqi, RiteOfResurrection, HeraldOfFrost
from .kamisato_ayaka import (
    KamisatoAyaka, FrostflakeSekiNoTo, KantenSenmyouBlessing
)


CryoCharactors = (
    Kaeya | Shenhe | Eula | Chongyun | Ganyu | Qiqi | KamisatoAyaka
)
SummonsOfCryoCharactors = (
    TalismanSpirit | TalismanSpirit | LightfallSword | SacredCryoPearl
    | HeraldOfFrost | FrostflakeSekiNoTo
)
CryoCharactorTalents = (
    ColdBloodedStrike | MysticalAbandon | WellspringOfWarLust | SteadyBreathing
    | UndividedHeart | RiteOfResurrection | KantenSenmyouBlessing
)
