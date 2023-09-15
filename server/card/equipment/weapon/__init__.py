from .vanilla import VanillaWeapon
from .other_claymore import Claymores
from .other_catalyst import Catalysts
from .other_polearm import Polearms
from .old_version import OldVersionWeapons


Weapons = (
    VanillaWeapon | Claymores | Catalysts | Polearms
    # Finally old version weapons
    | OldVersionWeapons
)
