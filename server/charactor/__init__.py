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
from .geo import (
    GeoCharactorTalents, GeoCharactors, SummonsOfGeoCharactors
)


Charactors = (
    Mob | PhysicalMob | MobMage | ElectroCharactors | HydroCharactors
    | DendroCharactors | GeoCharactors
)
SummonsOfCharactors = (
    SummonsOfElectroCharactors | SummonsOfHydroCharactors
    | SummonsOfGeoCharactors
)
CharactorTalents = (
    ElectroCharactorTalents | HydroCharactorTalents | DendroCharactorTalents
    | GeoCharactorTalents
)
