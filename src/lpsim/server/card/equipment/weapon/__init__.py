from .favonius import FavoniusWeapons
from .skyward import SkywardWeapons
from .vanilla import VanillaWeapon
from .sacrificial import SacrificialWeapons
from .sumeru_forge_weapon import SumeruForgeWeapons
from .other_claymore import Claymores
from .other_catalyst import Catalysts
from .other_polearm import Polearms
from .other_bow import Bows
from .other_sword import Swords
from .old_version import OldVersionWeapons


Weapons = (
    VanillaWeapon | SacrificialWeapons | Catalysts | Bows | Claymores 
    | Polearms | Swords | SkywardWeapons | FavoniusWeapons | SumeruForgeWeapons
    # Finally old version weapons
    | OldVersionWeapons
)
