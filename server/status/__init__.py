"""
All status.
"""

from ..object_base import TeamStatusBase, CharactorStatusBase
from .team_status.base import UsageTeamStatus, RoundTeamStatus
from .team_status.system import SystemTeamStatus
from .team_status.old_version import OldVersionTeamStatus


TeamStatus = (
    TeamStatusBase | UsageTeamStatus | RoundTeamStatus | SystemTeamStatus
    # finally, old version status
    | OldVersionTeamStatus
)
CharactorStatus = CharactorStatusBase | CharactorStatusBase
