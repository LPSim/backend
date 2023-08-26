from .mob import Mob
from .physical_mob import PhysicalMob
from .mob_mage import MobMage
from .electro import (
    ElectroCharactorTalents, ElectroCharactors, SummonsOfElectroCharactors
)


Charactors = Mob | PhysicalMob | MobMage | ElectroCharactors
SummonsOfCharactors = SummonsOfElectroCharactors | SummonsOfElectroCharactors
CharactorTalents = ElectroCharactorTalents | ElectroCharactorTalents
