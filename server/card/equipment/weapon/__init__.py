from .vanilla import VanillaWeapon
from .sacrificial import SacrificialWeapons
from .other_claymore import Claymores
from .other_catalyst import Catalysts
from .other_polearm import Polearms
from .other_bow import Bows
from .old_version import OldVersionWeapons


Weapons = (
    VanillaWeapon | SacrificialWeapons | Catalysts | Bows | Claymores 
    | Polearms
    # Finally old version weapons
    | OldVersionWeapons
)
