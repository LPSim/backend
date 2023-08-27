from .mob import Mob
from .physical_mob import PhysicalMob
from .mob_mage import MobMage
from .electro import (
    ElectroCharactorTalents, ElectroCharactors, SummonsOfElectroCharactors
)
from .hydro import (
    HydroCharactorTalents, HydroCharactors, SummonsOfHydroCharactors
)


Charactors = Mob | PhysicalMob | MobMage | ElectroCharactors | HydroCharactors
SummonsOfCharactors = SummonsOfElectroCharactors | SummonsOfHydroCharactors
CharactorTalents = ElectroCharactorTalents | HydroCharactorTalents
