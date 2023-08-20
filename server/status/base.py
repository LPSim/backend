from typing import Literal
from ..consts import ObjectType
from ..object_base import ObjectBase


class StatusBase(ObjectBase):
    """
    Base class of status.
    """
    name: str
    version: str
    show_usage: bool = True
    usage: int
    max_usage: int
    type: Literal[ObjectType.CHARACTOR_STATUS, ObjectType.TEAM_STATUS]
    renew_type: Literal['ADD', 'RESET', 'RESET_WITH_MAX'] = 'ADD'

    def renew(self, new_status: 'StatusBase') -> None:
        """
        Renew the status. It will copy the usage from the new status.
        """
        assert self.renew_type == 'ADD'  # now should be ADD
        self.usage += new_status.usage
        if self.max_usage < self.usage:
            self.usage = self.max_usage
