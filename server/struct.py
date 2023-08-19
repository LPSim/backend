from typing import List

from utils import BaseModel
from .consts import ObjectPositionType


class SkillActionArguments(BaseModel):
    """
    Arguments used in getting skill actions.
    """
    player_id: int
    our_active_charactor_id: int
    enemy_active_charactor_id: int
    our_charactors: List[int]
    enemy_charactors: List[int]


class ObjectPosition(BaseModel):
    """
    Position of an object in the game table, which will be set at initializing
    or updated when its position changes. Current change event: card go from
    deck to hand, from hand to deck, from hand to charactor, from charactor to
    hand, from hand to support, from support to support.
    Note the index of the object is not included (n-th summon from player 1's
    sommon lists) as it will change when some action triggered, for example
    RemoveSummonAction. For these actions, we will use the id of the object
    to identify. Position is used for objects to decide whether to respond
    events.
    """
    player_id: int
    charactor_id: int
    area: ObjectPositionType
