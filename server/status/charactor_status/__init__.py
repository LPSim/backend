from .system import SystemCharactorStatus
from .dendro_charactors import DendroCharactorStatus
from .geo_charactors import GeoCharactorStatus
from .foods import FoodStatus


CharactorStatus = (
    DendroCharactorStatus | GeoCharactorStatus
    | SystemCharactorStatus | FoodStatus
)
