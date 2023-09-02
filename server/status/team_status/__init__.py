from .system import SystemTeamStatus
from .hydro_charactors import HydroCharactorTeamStatus
from .dendro_charactors import DendroTeamStatus
from .geo_charactors import GeoTeamStatus
from .event_cards import EventCardTeamStatus

from .old_version import OldVersionTeamStatus


TeamStatus = (
    SystemTeamStatus | HydroCharactorTeamStatus | DendroTeamStatus
    | GeoTeamStatus | EventCardTeamStatus
    # finally, old version status
    | OldVersionTeamStatus
)
