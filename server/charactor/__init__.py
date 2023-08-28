from .mob import Mob
from .physical_mob import PhysicalMob
from .mob_mage import MobMage
from .electro import (
    ElectroCharactorTalents, ElectroCharactors, SummonsOfElectroCharactors
)
from .hydro import (
    HydroCharactorTalents, HydroCharactors, SummonsOfHydroCharactors
)
from .dendro import (
    DendroCharactorTalents, DendroCharactors,  # SummonsOfDendroCharactors
)


Charactors = (
    Mob | PhysicalMob | MobMage | ElectroCharactors | HydroCharactors
    | DendroCharactors
)
SummonsOfCharactors = SummonsOfElectroCharactors | SummonsOfHydroCharactors
CharactorTalents = (
    ElectroCharactorTalents | HydroCharactorTalents | DendroCharactorTalents
)
