"""
For each charactor, the newest version of charactor itself, summons, skills,
and talents are defined in its file. For old versions, they are defined in
old_version file, and the order of them should follow the version of them,
the older the later, so when specifying a version, newer version objects will
always be accepted earlier than older version objects.
"""
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
    PyroCharactorTalents, PyroCharactors, SummonsOfPyroCharactors
)
from .anemo import (
    AnemoCharactorTalents, AnemoCharactors, SummonsOfAnemoCharactors
)
from .cryo import (
    CryoCharactorTalents, CryoCharactors, SummonsOfCryoCharactors
)
from .old_version import (
    OldSummons, OldTalents, OldCharactors
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
    | SummonsOfPyroCharactors
    # Finally old summons
    | OldSummons
)
CharactorTalents = (
    ElectroCharactorTalents | HydroCharactorTalents | DendroCharactorTalents
    | GeoCharactorTalents | PyroCharactorTalents | AnemoCharactorTalents
    | CryoCharactorTalents
    # finally old talents
    | OldTalents
)
