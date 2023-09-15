from .vanilla import VanillaWeapon
from .other_claymore import Claymores
from .other_catalyst import Catalysts
from .other_polearm import Polearms
from .other_bow import Bows
from .old_version import OldVersionWeapons


Weapons = (
    VanillaWeapon | Claymores | Catalysts | Polearms | Bows
    # Finally old version weapons
    | OldVersionWeapons
)
