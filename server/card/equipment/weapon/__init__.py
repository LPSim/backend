from .vanilla import VanillaWeapon
from .other_claymore import Claymores
from .other_catalyst import Catalysts
from .other_polearm import Polearms


Weapons = VanillaWeapon | Claymores | Catalysts | Polearms
