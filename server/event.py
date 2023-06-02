from utils import BaseModel
from typing import Literal
from enum import Enum


class Events(Enum):
    EMPTY = 'EMPTY'


class EventArgumentsBase(BaseModel):
    """
    Base class of event arguments. event arguments are generated when new
    Action is triggered by events. It will record nesessary information about
    the event.
    """
    name: Literal['EventArgumentsBase'] = 'EventArgumentsBase'


EventArguments = EventArgumentsBase | EventArgumentsBase
