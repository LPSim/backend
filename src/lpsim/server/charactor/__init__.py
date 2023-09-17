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
    CryoCharactors | HydroCharactors | PyroCharactors | ElectroCharactors
    | AnemoCharactors | GeoCharactors | DendroCharactors
    # Mobs
    | Mob | PhysicalMob | MobMage
    # finally old charactors
    | OldCharactors
)
SummonsOfCharactors = (
    SummonsOfCryoCharactors | SummonsOfHydroCharactors
    | SummonsOfPyroCharactors | SummonsOfElectroCharactors
    | SummonsOfAnemoCharactors | SummonsOfGeoCharactors
    | SummonsOfDendroCharactors
    # Finally old summons
    | OldSummons
)
CharactorTalents = (
    CryoCharactorTalents | HydroCharactorTalents
    | PyroCharactorTalents | ElectroCharactorTalents
    | AnemoCharactorTalents | GeoCharactorTalents
    | DendroCharactorTalents
    # finally old talents
    | OldTalents
)
