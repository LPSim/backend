from .system import SystemTeamStatus
from .hydro_charactors import HydroCharactorTeamStatus
from .dendro_charactors import DendroTeamStatus
from .geo_charactors import GeoTeamStatus
from .anemo_charactors import AnemoTeamStatus
from .pyro_charactors import PyroTeamStatus
from .cryo_charactors import CryoTeamStatus
from .event_cards import EventCardTeamStatus
from .weapons import WeaponTeamStatus

from .old_version import OldVersionTeamStatus


TeamStatus = (
    SystemTeamStatus | HydroCharactorTeamStatus | DendroTeamStatus
    | GeoTeamStatus | AnemoTeamStatus | PyroTeamStatus | CryoTeamStatus 
    | EventCardTeamStatus | WeaponTeamStatus
    # finally, old version status
    | OldVersionTeamStatus
)
