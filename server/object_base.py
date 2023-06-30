from utils import BaseModel
from typing import List
from enum import Enum
from .action import ActionTypes


class ObjectType(Enum):
    EMPTY = 'EMPTY'
    CHARACTOR = 'CHARACTOR'
    DICE = 'DICE'
    DECK_CARD = 'DECK_CARD'
    HAND_CARD = 'HAND_CARD'
    SUMMON = 'SUMMON'
    SUPPORT = 'SUPPORT'
    SKILL = 'SKILL'
    WEAPON = 'WEAPON'
    ARTIFACT = 'ARTIFACT'
    TALENT = 'TALENT'
    CHARACTOR_BUFF = 'CHARACTOR_BUFF'
    TEAM_BUFF = 'TEAM_BUFF'

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return self.value


class ObjectBase(BaseModel):
    """
    Base class of objects in the game table. All objects in the game table 
    should inherit from this class.
    """
    type: ObjectType = ObjectType.EMPTY
    player_id: int = -1
    index: int = 0
    _object_id: int = -1
    event_triggers: List[ActionTypes] = []
