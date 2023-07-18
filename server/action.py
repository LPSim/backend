from enum import Enum
from utils import BaseModel
from typing import Literal, List
from .interaction import (
    ResponseBase,
    ChooseCharactorResponse,
    RerollDiceResponse,
    DeclareRoundEndResponse,
    SwitchCharactorResponse,
)
from .consts import DieColor


class ActionTypes(str, Enum):
    EMPTY = 'EMPTY'
    DRAW_CARD = 'DRAW_CARD'
    RESTORE_CARD = 'RESTORE_CARD'
    REMOVE_CARD = 'REMOVE_CARD'
    CHOOSE_CHARACTOR = 'CHOOSE_CHARACTOR'
    CREATE_DICE = 'CREATE_DICE'
    REMOVE_DICE = 'REMOVE_DICE'
    DECLARE_ROUND_END = 'DECLARE_ROUND_END'
    COMBAT_ACTION = 'COMBAT_ACTION'
    SWITCH_CHARACTOR = 'SWITCH_CHARACTOR'

    # system phase actions
    ROUND_PREPARE = 'ROUND_PREPARE'


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


class RemoveCardAction(ActionBase):
    """
    Action for removing cards.
    """
    type: Literal[ActionTypes.REMOVE_CARD] = ActionTypes.REMOVE_CARD
    player_id: int
    card_id: int
    card_position: Literal['HAND', 'DECK']
    remove_type: Literal['USED', 'BURNED']


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


class CreateDiceAction(ActionBase):
    """
    Action for creating dice.

    Args:
        player_id (int): The ID of the player to create the dice for.
        number (int): The number of dice to create.
        color (DieColor | None): The color of the dice to create. If None,
            the following generate rules will be activated.
        random (bool): Whether to randomly generate the color of dice.
        different (bool): Whether to generate different colors of dice.
    """
    type: Literal[ActionTypes.CREATE_DICE] = ActionTypes.CREATE_DICE
    player_id: int
    number: int
    color: DieColor | None = None
    random: bool = False
    different: bool = False


class RemoveDiceAction(ActionBase):
    """
    Action for removing dice.

    Args:
        player_id (int): The ID of the player to remove the dice for.
        dice_ids (List[int]): The IDs of the dice to remove.
    """
    type: Literal[ActionTypes.REMOVE_DICE] = ActionTypes.REMOVE_DICE
    player_id: int
    dice_ids: List[int]

    @classmethod
    def from_response(cls, response: RerollDiceResponse):
        """
        Generate RemoveDiceAction from RerollDiceResponse.
        TODO: from other responses, i.e. use skill response.
        """
        return cls(
            object_id = -1,
            player_id = response.player_id,
            dice_ids = response.reroll_dice_ids,
        )


class DeclareRoundEndAction(ActionBase):
    """
    Action for declaring the end of the round.
    """
    type: Literal[ActionTypes.DECLARE_ROUND_END] = \
        ActionTypes.DECLARE_ROUND_END
    player_id: int

    @classmethod
    def from_response(cls, response: DeclareRoundEndResponse):
        """
        Generate DeclareRoundEndAction from DeclareRoundEndResponse.
        """
        return cls(
            object_id = -1,
            player_id = response.player_id,
        )


class CombatActionAction(ActionBase):
    """
    Action for combat.
    """
    type: Literal[ActionTypes.COMBAT_ACTION] = ActionTypes.COMBAT_ACTION
    player_id: int

    @classmethod
    def from_response(cls, response: ResponseBase):
        """
        Generate CombatActionAction from Responses.
        """
        return cls(
            object_id = -1,
            player_id = response.player_id,
        )


class SwitchCharactorAction(ActionBase):
    """
    Action for switching charactor.
    """
    type: Literal[ActionTypes.SWITCH_CHARACTOR] = ActionTypes.SWITCH_CHARACTOR
    player_id: int
    charactor_id: int

    @classmethod
    def from_response(cls, response: SwitchCharactorResponse):
        """
        Generate SwitchCharactorAction from SwitchCharactorResponse.
        """
        return cls(
            object_id = -1,
            player_id = response.player_id,
            charactor_id = response.charactor_id,
        )
