from typing import Literal, List
from ...consts import ObjectType
from ..base import StatusBase
from ...action import RemoveObjectAction, Actions
from ...event import MakeDamageEventArguments, RoundEndEventArguments


class CharactorStatusBase(StatusBase):
    """
    Base class of charactor status.
    """
    type: Literal[ObjectType.CHARACTOR_STATUS] = ObjectType.CHARACTOR_STATUS


class UsageCharactorStatus(CharactorStatusBase):
    """
    Base class of team status that based on usages.
    It will implement a method to check if run out of usage; when run out
    of usage, it will remove itself.

    By default, it listens to MAKE_DAMAGE event to check if run out of usage,
    as most usage-based status will decrease usage when damage made.
    Not using AFTER_MAKE_DAMAGE because we should remove the status before
    side effects of elemental reaction, which is triggered on RECEVIE_DAMAGE.

    If it is not a damage related status, check_remove_triggered should be
    called manually.
    """
    name: Literal['UsageCharactorStatus'] = 'UsageCharactorStatus'

    def check_remove_triggered(self) -> List[Actions]:
        """
        Check if the status should be removed.
        when usage has changed, call this function to check if the status
        should be removed.
        """
        if self.usage <= 0:
            return [RemoveObjectAction(
                object_position = self.position,
            )]
        return []

    def event_handler_MAKE_DAMAGE(
            self, event: MakeDamageEventArguments) -> List[Actions]:
        """
        When damage made, check whether the team status should be removed.
        """
        return self.check_remove_triggered()


class RoundCharactorStatus(CharactorStatusBase):
    """
    Base class of team status that based on rounds.  It will implement the 
    event trigger on ROUND_END to check if run out of usages; when run out
    of usages, it will remove itself.
    """
    name: Literal['RoundCharactorStatus'] = 'RoundCharactorStatus'
    usage: int

    def check_should_remove(self) -> List[RemoveObjectAction]:
        """
        Check if the status should be removed.
        when round has changed, call this function to check if the status
        should be removed.
        """
        if self.usage <= 0:
            return [RemoveObjectAction(
                object_position = self.position,
            )]
        return []

    def event_handler_ROUND_END(self, event: RoundEndEventArguments) \
            -> List[Actions]:
        """
        After round ending, check whether the round status should be removed.
        """
        self.usage -= 1
        return list(self.check_should_remove())
