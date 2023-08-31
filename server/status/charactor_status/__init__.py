from .system import SystemCharactorStatus
from .dendro_charactors import DendroCharactorStatus
from .foods import FoodStatus


CharactorStatus = SystemCharactorStatus | DendroCharactorStatus | FoodStatus
