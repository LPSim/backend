from .system import SystemTeamStatus
from .hydro_charactors import HydroCharactorTeamStatus
from .dendro_charactors import DendroTeamStatus
from .geo_charactors import GeoTeamStatus
from .anemo_charactors import AnemoTeamStatus
from .pyro_charactors import PyroTeamStatus
from .event_cards import EventCardTeamStatus
from .weapons import WeaponTeamStatus

from .old_version import OldVersionTeamStatus


TeamStatus = (
    SystemTeamStatus | HydroCharactorTeamStatus | DendroTeamStatus
    | GeoTeamStatus | AnemoTeamStatus | PyroTeamStatus | EventCardTeamStatus 
    | WeaponTeamStatus
    # finally, old version status
    | OldVersionTeamStatus
)
