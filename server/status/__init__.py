"""
All status.
"""

from .charactor_status.system import SystemCharactorStatus
from .team_status.system import SystemTeamStatus
from .team_status.old_version import OldVersionTeamStatus


CharactorStatus = (
    SystemCharactorStatus | SystemCharactorStatus
)
TeamStatus = (
    SystemTeamStatus
    # finally, old version status
    | OldVersionTeamStatus
)
