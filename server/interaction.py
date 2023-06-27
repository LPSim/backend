from utils import BaseModel
from typing import Literal, List
from enum import Enum


class RequestType(Enum):
    """
    Enum representing the type of a request.

    Attributes:
        SYSTEM (str): The request is a system request, e.g. roll dices, choose
            front charactor, change cards. It should not be mixed with the 
            following types.
        BATTLE (str): The request is a battle request, e.g. use skill, use
            talent card, switch charactor.
        QUICK (str): The request is a quick request, e.g. play a event card,
            switch charactor with Leave It To Me, attack with Wind and Freedom.
    """
    SYSTEM = 'SYSTEM'
    BATTLE = 'BATTLE'
    QUICK = 'QUICK'


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


Responses = ResponseBase | SwitchCardResponse | ChooseCharactorResponse


Requests = RequestBase | SwitchCardRequest | ChooseCharactorRequest
