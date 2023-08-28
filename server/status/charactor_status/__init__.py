from .system import SystemCharactorStatus
from .dendro_charactors import DendroCharactorStatus


CharactorStatus = SystemCharactorStatus | DendroCharactorStatus
