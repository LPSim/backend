from .vanilla import VanillaWeapon
from .other_claymore import Claymores
from .other_catalyst import Catalysts


Weapons = VanillaWeapon | Claymores | Catalysts
