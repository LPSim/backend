from .system import SystemTeamStatus
from .hydro_charactors import HydroCharactorTeamStatus
from .dendro_charactors import DendroTeamStatus

from .old_version import OldVersionTeamStatus


TeamStatus = (
    SystemTeamStatus | HydroCharactorTeamStatus | DendroTeamStatus
    # finally, old version status
    | OldVersionTeamStatus
)
