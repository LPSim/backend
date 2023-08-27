from .system import SystemTeamStatus
from .hydro_charactors import HydroCharactorTeamStatus

from .old_version import OldVersionTeamStatus


TeamStatus = (
    SystemTeamStatus | HydroCharactorTeamStatus
    # finally, old version status
    | OldVersionTeamStatus
)
