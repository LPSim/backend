from .mob import Mob
from .physical_mob import PhysicalMob
from .mob_mage import MobMage


Charactors = Mob | PhysicalMob | MobMage
