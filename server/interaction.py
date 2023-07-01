from utils import BaseModel
from typing import Literal, List
from enum import Enum
from .consts import DieColor


class RequestType(Enum):
    """
    Enum representing the type of a request.

    Attributes:
        SYSTEM (str): The request is a system request, e.g. roll dice, choose
            active charactor, change cards. It should not be mixed with the 
            following types.
        BATTLE (str): The request is a battle request, e.g. use skill, use
            talent card, switch charactor.
        QUICK (str): The request is a quick request, e.g. play a event card,
            switch charactor with Leave It To Me, attack with Wind and Freedom.
    """
    SYSTEM = 'SYSTEM'
    BATTLE = 'BATTLE'
    QUICK = 'QUICK'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class RequestBase(BaseModel):
    """
    Base class of request.
    """
    name: Literal['RequestBase'] = 'RequestBase'
    type: RequestType
    player_id: int


class SwitchCardRequest(RequestBase):
    name: Literal['SwitchCardRequest'] = 'SwitchCardRequest'
    type: Literal[RequestType.SYSTEM] = RequestType.SYSTEM
    card_names: List[str]
    maximum_switch_number: int = 999


class ChooseCharactorRequest(RequestBase):
    name: Literal['ChooseCharactorRequest'] = 'ChooseCharactorRequest'
    type: Literal[RequestType.SYSTEM] = RequestType.SYSTEM
    available_charactor_ids: List[int]


class RerollDiceRequest(RequestBase):
    """
    Request for reroll dice.

    Args:
        colors (List[DieColor]): The colors of the dice to reroll.
        reroll_times (int): The times of reroll. In one time, player can choose
            any number of dice to reroll, and after one reroll, the reroll
            times will decrease by 1. If it reaches 0, the request is removed.
    """
    name: Literal['RerollDiceRequest'] = 'RerollDiceRequest'
    type: Literal[RequestType.SYSTEM] = RequestType.SYSTEM
    colors: List[DieColor]
    reroll_times: int


class ResponseBase(BaseModel):
    """
    Base class of response.
    """
    name: Literal['ResponseBase'] = 'ResponseBase'
    request: RequestBase

    @property
    def player_id(self) -> int:
        """
        Return the player id of the response.
        """
        return self.request.player_id

    def is_valid(self) -> bool:
        """
        Check whether the response is valid.
        """
        return True


class SwitchCardResponse(ResponseBase):
    """
    Card ids want to switch, based on the request.
    """
    name: Literal['SwitchCardResponse'] = 'SwitchCardResponse'
    request: SwitchCardRequest
    card_ids: List[int]

    @property
    def is_valid(self) -> bool:
        if len(self.card_ids) > self.request.maximum_switch_number:
            return False
        if len(set(self.card_ids)) != len(self.card_ids):
            return False
        for i in self.card_ids:
            if i < 0 or i >= len(self.request.card_names):
                return False
        return True

    @property
    def card_names(self) -> List[str]:
        """
        Return the card names of the response.
        """
        return [self.request.card_names[i] for i in self.card_ids]


class ChooseCharactorResponse(ResponseBase):
    name: Literal['ChooseCharactorResponse'] = 'ChooseCharactorResponse'
    request: ChooseCharactorRequest
    charactor_id: int

    @property
    def is_valid(self) -> bool:
        return self.charactor_id in self.request.available_charactor_ids


class RerollDiceResponse(ResponseBase):
    name: Literal['RerollDiceResponse'] = 'RerollDiceResponse'
    request: RerollDiceRequest
    reroll_dice_ids: List[int]

    @property
    def is_valid(self) -> bool:
        """
        if have duplicate dice ids, or dice ids out of range, return False.
        """
        if len(self.reroll_dice_ids) != len(set(self.reroll_dice_ids)):
            return False
        if max(self.reroll_dice_ids) >= len(self.request.colors):
            return False
        if min(self.reroll_dice_ids) < 0:
            return False
        return True


Responses = (
    ResponseBase | SwitchCardResponse | ChooseCharactorResponse
    | RerollDiceResponse
)


Requests = (
    RequestBase | SwitchCardRequest | ChooseCharactorRequest
    | RerollDiceRequest
)
