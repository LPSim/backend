from typing import Literal
from ...consts import ObjectType
from ..base import StatusBase


class CharactorStatusBase(StatusBase):
    """
    Base class of charactor status.
    """
    type: Literal[ObjectType.CHARACTOR_STATUS] = ObjectType.CHARACTOR_STATUS
