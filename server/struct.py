from typing import List, Literal

from utils import BaseModel
from .consts import (
    ObjectPositionType, DamageType, DamageElementalType, DamageSourceType
)


class DamageValue(BaseModel):
    """
    It declares a damage, i.e. damge is received by active/back charactor,
    it will change active charactor with what rule.

    Args:
        player_id (int): The player id of the player who declares the damage.
        damage_type (DamageType): The type of the damage.
        damage_source_type (DamageSourceType): The source type of the damage.
        damage (int): The damage value.
        damage_elemental_type (DamageElementalType): The elemental type of the
            damage.
        charge_cost (int): The charge cost of the damage.
        target_player (Literal['CURRENT', 'ENEMY']): The player who will
            receive the damage.
        target_charactor (Literal['ACTIVE', 'BACK', 'NEXT', 'PREV', 
            'ABSOLUTE']): The charactor who will receive the damage.
            If it is defeated, this damage will be ignored.
        target_charactor_id (int): The charactor id of the charactor who will
            receive the damage. Only used when target_charactor is 'ABSOLUTE'.
    """

    player_id: int
    damage_type: DamageType
    damage_source_type: DamageSourceType
    damage: int
    damage_elemental_type: DamageElementalType
    charge_cost: int

    # damage which player
    target_player: Literal['CURRENT', 'ENEMY']
    target_charactor: Literal['ACTIVE', 'BACK', 'NEXT', 'PREV', 'ABSOLUTE']
    target_charactor_id: int = -1


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
