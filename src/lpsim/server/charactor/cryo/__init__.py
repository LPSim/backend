from .kaeya import Kaeya, ColdBloodedStrike
from .shenhe import Shenhe, MysticalAbandon, TalismanSpirit
from .eula import Eula, LightfallSword, WellspringOfWarLust
from .chongyun import Chongyun, SteadyBreathing
from .ganyu import Ganyu, SacredCryoPearl, UndividedHeart
from .qiqi import Qiqi, RiteOfResurrection, HeraldOfFrost
from .kamisato_ayaka import (
    KamisatoAyaka, FrostflakeSekiNoTo, KantenSenmyouBlessing
)
from .diona import Diona, DrunkenMist, ShakenNotPurred
from .fatui_cryo_cicin_mage import (
    FatuiCryoCicinMage, CryoCicins, CicinsColdGlare
)


CryoCharactors = (
    Ganyu | Diona | Kaeya | Chongyun | KamisatoAyaka | Eula | Shenhe | Qiqi
    # finally monsters
    | FatuiCryoCicinMage
)
SummonsOfCryoCharactors = (
    SacredCryoPearl | DrunkenMist | FrostflakeSekiNoTo | LightfallSword 
    | TalismanSpirit | HeraldOfFrost
    # finally monsters
    | CryoCicins
)
CryoCharactorTalents = (
    UndividedHeart | ShakenNotPurred | ColdBloodedStrike | SteadyBreathing 
    | KantenSenmyouBlessing | WellspringOfWarLust | MysticalAbandon
    | RiteOfResurrection
    # finally monsters
    | CicinsColdGlare
)
