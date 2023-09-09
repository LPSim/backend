from .kaeya import Kaeya, ColdBloodedStrike
from .shenhe import Shenhe, MysticalAbandon, TalismanSpirit
from .eula import Eula, LightfallSword, WellspringOfWarLust


CryoCharactors = Kaeya | Shenhe | Eula
SummonsOfCryoCharactors = TalismanSpirit | TalismanSpirit | LightfallSword
CryoCharactorTalents = (
    ColdBloodedStrike | MysticalAbandon | WellspringOfWarLust
)
