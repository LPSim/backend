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
    DendroCharactorTalents, DendroCharactors, SummonsOfDendroCharactors
)
from .geo import (
    GeoCharactorTalents, GeoCharactors, SummonsOfGeoCharactors
)
from .pyro import (
    PyroCharactorTalents, PyroCharactors,  # SummonsOfPyroCharactors
)
from .anemo import (
    AnemoCharactorTalents, AnemoCharactors, SummonsOfAnemoCharactors
)
from .cryo import (
    CryoCharactorTalents, CryoCharactors, SummonsOfCryoCharactors
)
from .old_version import (
    OldTalents, OldCharactors
)


Charactors = (
    Mob | PhysicalMob | MobMage | ElectroCharactors | HydroCharactors
    | DendroCharactors | GeoCharactors | PyroCharactors | AnemoCharactors
    | CryoCharactors
    # finally old charactors
    | OldCharactors
)
SummonsOfCharactors = (
    SummonsOfElectroCharactors | SummonsOfHydroCharactors
    | SummonsOfDendroCharactors | SummonsOfGeoCharactors
    | SummonsOfAnemoCharactors | SummonsOfCryoCharactors
)
CharactorTalents = (
    ElectroCharactorTalents | HydroCharactorTalents | DendroCharactorTalents
    | GeoCharactorTalents | PyroCharactorTalents | AnemoCharactorTalents
    | CryoCharactorTalents
    # finally old talents
    | OldTalents
)
