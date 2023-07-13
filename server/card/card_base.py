from server.object_base import ObjectBase, ObjectType
from server.action import ActionBase
from typing import Literal, List


class CardBase(ObjectBase):
    """
    Base class of all real cards. 
    """
    name: str
    type: Literal[ObjectType.DECK_CARD, ObjectType.HAND_CARD] = \
        ObjectType.DECK_CARD

    def act(self) -> List[ActionBase]:
        """
        Act the card. It will return a list of actions.
        """
        raise NotImplementedError()
