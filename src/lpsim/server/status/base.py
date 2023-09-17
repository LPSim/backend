from typing import Literal
from ..consts import ObjectType
from ..object_base import ObjectBase


class StatusBase(ObjectBase):
    """
    Base class of status.
    """
    name: str
    desc: str
    version: str
    show_usage: bool = True
    usage: int
    max_usage: int
    type: Literal[ObjectType.CHARACTOR_STATUS, ObjectType.TEAM_STATUS]
    renew_type: Literal['ADD', 'RESET', 'RESET_WITH_MAX'] = 'ADD'

    def renew(self, new_status: 'StatusBase') -> None:
        """
        Renew the status. 
        """
        assert self.renew_type == 'ADD', 'Other types not tested'
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
