from .system import SystemCharactorStatus
from .dendro_charactors import DendroCharactorStatus
from .geo_charactors import GeoCharactorStatus
from .foods import FoodStatus
from .artifacts import ArtifactCharactorStatus
from .event_cards import EventCardCharactorStatus


CharactorStatus = (
    DendroCharactorStatus | GeoCharactorStatus
    | SystemCharactorStatus | FoodStatus | ArtifactCharactorStatus
    | EventCardCharactorStatus
)
