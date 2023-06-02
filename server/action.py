from utils import BaseModel
from typing import Literal
from server.event import EventArguments


class ActionBase(BaseModel):
    """
    Base class for game actions.

    Attributes:
        name (Literal['ActionBase']): The name of the action.
        object_id (int): The ID of the object associated with the action.
        event_arguments (EventArguments): The arguments for the event that 
            triggered the action.
    """
    name: Literal['ActionBase'] = 'ActionBase'
    object_id: int
    event_arguments: EventArguments


Action = ActionBase | ActionBase
