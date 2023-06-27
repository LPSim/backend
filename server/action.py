from enum import Enum
from utils import BaseModel
from typing import Literal, List
from .interaction import (
    ChooseCharactorResponse,
)


class ActionTypes(Enum):
    EMPTY = 'EMPTY'
    DRAW_CARD = 'DRAW_CARD'
    RESTORE_CARD = 'RESTORE_CARD'
    CHOOSE_CHARACTOR = 'CHOOSE_CHARACTOR'


class ActionBase(BaseModel):
    """
    Base class for game actions.
    An action contains arguments to make changes to the game table.

    Attributes:
        action_type (Literal[ActionTypes]): The type of the action.
        object_id (int): The ID of the object associated with the action.
            -1 means action from the system or from response.
    """
    type: Literal[ActionTypes.EMPTY] = ActionTypes.EMPTY
    object_id: int


class DrawCardAction(ActionBase):
    """
    Action for drawing cards.
    """
    type: Literal[ActionTypes.DRAW_CARD] = ActionTypes.DRAW_CARD
    player_id: int
    number: int


class RestoreCardAction(ActionBase):
    """
    Action for restoring cards.
    """
    type: Literal[ActionTypes.RESTORE_CARD] = ActionTypes.RESTORE_CARD
    player_id: int
    card_ids: List[int]


class ChooseCharactorAction(ActionBase):
    """
    Action for choosing charactors.
    """
    type: Literal[ActionTypes.CHOOSE_CHARACTOR] = ActionTypes.CHOOSE_CHARACTOR
    player_id: int
    charactor_id: int

    @classmethod
    def from_response(cls, response: ChooseCharactorResponse):
        """
        Generate ChooseCharactorAction from ChooseCharactorResponse.
        """
        return cls(
            object_id = -1,
            player_id = response.player_id,
            charactor_id = response.charactor_id,
        )


Actions = ActionBase | DrawCardAction | RestoreCardAction
