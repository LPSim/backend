from .old_version import OldVersionCharactorStatus
from .system import SystemCharactorStatus
from .pyro_charactors import PyroCharactorStatus
from .dendro_charactors import DendroCharactorStatus
from .geo_charactors import GeoCharactorStatus
from .electro_charactors import ElectroCharactorStatus
from .anemo_charactors import AnemoCharactorStatus
from .hydro_charactors import HydroCharactorStatus
from .cryo_charactors import CryoCharactorStatus
from .foods import FoodStatus
from .artifacts import ArtifactCharactorStatus
from .weapons import WeaponCharactorStatus
from .event_cards import EventCardCharactorStatus


CharactorStatus = (
    PyroCharactorStatus | DendroCharactorStatus | GeoCharactorStatus
    | ElectroCharactorStatus | AnemoCharactorStatus | HydroCharactorStatus
    | CryoCharactorStatus
    | SystemCharactorStatus | FoodStatus | ArtifactCharactorStatus
    | WeaponCharactorStatus | EventCardCharactorStatus
    # finally old versions
    | OldVersionCharactorStatus
)
