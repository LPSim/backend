from .kaeya import Kaeya, ColdBloodedStrike
from .shenhe import Shenhe, MysticalAbandon, TalismanSpirit
from .eula import Eula, LightfallSword, WellspringOfWarLust
from .chongyun import Chongyun, SteadyBreathing


CryoCharactors = Kaeya | Shenhe | Eula | Chongyun
SummonsOfCryoCharactors = TalismanSpirit | TalismanSpirit | LightfallSword
CryoCharactorTalents = (
    ColdBloodedStrike | MysticalAbandon | WellspringOfWarLust | SteadyBreathing
)
