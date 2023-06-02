import numpy as np
from typing import Literal, Tuple, List
from enum import Enum

from utils import BaseModel
from server.player_table import PlayerTable
from server.action import Action
from server.registry import Registry
from server.response import Responses


class MatchStatus(str, Enum):
    """
    Enum representing the status of a match.

    Attributes:
        INVALID (str): The match is invalid. Should not be used in common
            situations.
        WAITING (str): The match is waiting for start.
        START (str): The match starts, will decide who is the first player, 
            draw initial card, etc.
        PLAYER0_PLAY (str): Player 0 is deciding its action.
        PLAYER0_ACT (str): Player 0 decided its action, but action execution
            is interrupted and waiting for new inputs, e.g. character of
            player 1 is dead, and player 1 needs to choose a new character.
        PLAYER1_PLAY (str): Player 1 is deciding its action.
        PLAYER1_ACT (str): Player 1 decided its action, but action execution
            is interrupted and waiting for new inputs, e.g. character of
            player 0 is dead, and player 0 needs to choose a new character.
    """
    INVALID = 'invalid'
    WAITING = 'waiting'
    START = 'start'
    PLAYER0_PLAY = 'player0_play'
    PLAYER0_ACT = 'player0_act'
    PLAYER1_PLAY = 'player1_play'
    PLAYER1_ACT = 'player1_act'


class Match(BaseModel):
    """
    """

    name: Literal['Match'] = 'Match'

    # random state
    random_state: Tuple = ()
    _random_state: np.random.RandomState = np.random.RandomState()

    # match information
    round_number: int = 0
    player_tables: List[PlayerTable] = [PlayerTable(), PlayerTable()]
    match_status: MatchStatus = MatchStatus.WAITING
    action_queue: List[List[Action]] = []
    response_player: int = -1
    responses: List[Responses] = []

    # registry, all objects onPlayerTable will be registered. it will update
    # on initialization, object creation and deletion, gives a unique id for 
    # the object, and collect event triggers of object.
    _registry: Registry = Registry()

    def __init__(self):
        super().__init__()
        if self.random_state:
            self._random_state = np.random.RandomState(self.random_state)

    def random(self):
        """
        Return a random number ranges 0-1 based on random_state, and save new
        random state.
        """
        ret = self._random_state.random()
        self.random_state = self._random_state.get_state(
            legacy = True)  # type: ignore
        return ret
