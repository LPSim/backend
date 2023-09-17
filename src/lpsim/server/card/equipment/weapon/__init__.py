from .skyward import SkywardWeapons
from .vanilla import VanillaWeapon
from .sacrificial import SacrificialWeapons
from .other_claymore import Claymores
from .other_catalyst import Catalysts
from .other_polearm import Polearms
from .other_bow import Bows
from .other_sword import Swords
from .old_version import OldVersionWeapons


Weapons = (
    VanillaWeapon | SacrificialWeapons | Catalysts | Bows | Claymores 
    | Polearms | Swords | SkywardWeapons
    # Finally old version weapons
    | OldVersionWeapons
)
