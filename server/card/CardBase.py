from server.object_base import ObjectBase
from server.action import Actions
from typing import Literal, List


class CardBase(ObjectBase):
    """
    Base class of all real cards. 
    """
    name: Literal['CardBase'] = 'CardBase'

    def act(self) -> List[Actions]:
        """
        Act the card. It will return a list of actions.
        """
        raise NotImplementedError()
