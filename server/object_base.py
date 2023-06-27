from utils import BaseModel
from typing import List
from server.action import ActionTypes


class ObjectBase(BaseModel):
    """
    Base class of virtual cards. We treat all actions as cards, 
    e.g. charactor skills, charactor change, etc. These virtual cards will 
    not consider as real cards, and will not occupy the hand slots.
    """
    """
    Base class of objects in the game table. All objects in the game table 
    should inherit from this class.
    """
    name: str = 'ObjectBase'
    player_id: int = -1
    _object_id: int = -1
    event_triggers: List[ActionTypes] = []
