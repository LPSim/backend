"""
All status.
"""

from .charactor_status.base import CharactorStatusBase
from .team_status.base import TeamStatusBase, UsageTeamStatus, RoundTeamStatus
from .team_status.system import SystemTeamStatus
from .team_status.old_version import OldVersionTeamStatus


CharactorStatus = CharactorStatusBase | CharactorStatusBase
TeamStatus = (
    TeamStatusBase | UsageTeamStatus | RoundTeamStatus | SystemTeamStatus
    # finally, old version status
    | OldVersionTeamStatus
)
