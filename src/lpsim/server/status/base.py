from typing import Any, Literal
from pydantic import validator

from lpsim.server.action import Actions
from lpsim.server.event import CreateObjectEventArguments, RoundPrepareEventArguments

from ...utils import accept_same_or_higher_version
from ..consts import IconType
from ..object_base import ObjectBase


class StatusBase(ObjectBase):
    """
    Base class of status.
    """

    name: str
    strict_version_validation: bool = False  # default accept higher versions
    version: str
    show_usage: bool = True
    usage: int
    max_usage: int
    renew_type: Literal["ADD", "RESET", "RESET_WITH_MAX"] = "ADD"

    icon_type: IconType

    @validator("version", pre=True)
    def accept_same_or_higher_version(cls, v: str, values):
        return accept_same_or_higher_version(cls, v, values)

    def renew(self, new_status: "StatusBase") -> None:
        """
        Renew the status.
        """
        assert self.renew_type == "ADD", "Other types not tested"
        if self.max_usage < new_status.max_usage:
            self.max_usage = new_status.max_usage
        if self.max_usage <= self.usage:
            # currently over maximum, ignore renew.
            return
        self.usage += new_status.usage
        if self.max_usage < self.usage:
            self.usage = self.max_usage
        return
        # elif self.renew_type == 'RESET':
        #     self.usage = new_status.usage
        # elif self.renew_type == 'RESET_WITH_MAX':
        #     raise NotImplementedError('Not tested part')
        #     self.usage = max(self.usage, new_status.usage)


class UsageWithRoundRestrictionStatusBase(StatusBase):
    """
    Supports that restricts maximum usage per round, and also has total
    maximum usage. e.g. Grass Ring of Sanctification has 1 usage per round and 3 total
    usage.
    """

    usage_this_round: int = 0
    max_usage_one_round: int

    def renew(self, new_status: "UsageWithRoundRestrictionStatusBase") -> None:
        """
        Renew the status.
        """
        super().renew(new_status)
        if (
            self.max_usage_one_round < new_status.max_usage_one_round
        ):  # pragma: no cover  # noqa
            # refresh usage this round when renew
            self.max_usage_one_round = new_status.max_usage_one_round

    def event_handler_CREATE_OBJECT(
        self, event: CreateObjectEventArguments, match: Any
    ) -> list[Actions]:
        """
        when self created, set usage_this_round to max_usage_one_round
        """
        action = event.action
        if action.object_name == self.name and self.position.satisfy(
            "both pidx=same cidx=same area=same", target=action.object_position
        ):
            # self created
            self.usage_this_round = self.max_usage_one_round
        return []

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> list[Actions]:
        self.usage_this_round = self.max_usage_one_round
        return []

    def has_usage(self) -> bool:
        return self.usage > 0 and self.usage_this_round > 0

    def use(self) -> None:
        assert self.has_usage()
        self.usage -= 1
        self.usage_this_round -= 1
