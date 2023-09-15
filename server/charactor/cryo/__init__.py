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
    Ganyu | Kaeya | Chongyun | KamisatoAyaka | Eula | Shenhe | Qiqi
)
SummonsOfCryoCharactors = (
    SacredCryoPearl | FrostflakeSekiNoTo | LightfallSword | TalismanSpirit
    | HeraldOfFrost
)
CryoCharactorTalents = (
    UndividedHeart | ColdBloodedStrike | SteadyBreathing 
    | KantenSenmyouBlessing | WellspringOfWarLust | MysticalAbandon
    | RiteOfResurrection
)
