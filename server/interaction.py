from utils import BaseModel, list_unique_range_right
from typing import Literal, List, Any
from .consts import DieColor
from .struct import Cost, CardActionTarget


class RequestBase(BaseModel):
    """
    Base class of request.
    """
    name: Literal['RequestBase'] = 'RequestBase'
    player_id: int


class SwitchCardRequest(RequestBase):
    name: Literal['SwitchCardRequest'] = 'SwitchCardRequest'
    card_names: List[str]
    maximum_switch_number: int = 999


class ChooseCharactorRequest(RequestBase):
    name: Literal['ChooseCharactorRequest'] = 'ChooseCharactorRequest'
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
    colors: List[DieColor]
    reroll_times: int


class SwitchCharactorRequest(RequestBase):
    """
    Request for switch charactor. It can be combat or quick request.
    """
    name: Literal['SwitchCharactorRequest'] = 'SwitchCharactorRequest'
    active_charactor_id: int
    candidate_charactor_ids: List[int]
    dice_colors: List[DieColor]
    cost: Cost


class ElementalTuningRequest(RequestBase):
    """
    Request for elemental tuning.
    """
    name: Literal['ElementalTuningRequest'] = 'ElementalTuningRequest'
    dice_colors: List[DieColor]
    dice_ids: List[int]
    card_ids: List[int]


class DeclareRoundEndRequest(RequestBase):
    """
    Request for declare round end.
    """
    name: Literal['DeclareRoundEndRequest'] = 'DeclareRoundEndRequest'


class UseSkillRequest(RequestBase):
    """
    Request for use skill.
    """
    name: Literal['UseSkillRequest'] = 'UseSkillRequest'
    charactor_id: int
    skill_id: int
    dice_colors: List[DieColor]
    cost: Cost


class UseCardRequest(RequestBase):
    """
    Request for use card.
    """
    name: Literal['UseCardRequest'] = 'UseCardRequest'
    card_id: int
    dice_colors: List[DieColor]
    targets: List[CardActionTarget]
    cost: Cost


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

    def is_valid(self, match: Any) -> bool:
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

    def is_valid(self, match: Any) -> bool:
        if len(self.card_ids) > self.request.maximum_switch_number:
            return False
        return list_unique_range_right(
            self.card_ids, minn = 0, maxn = len(self.request.card_names))

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

    def is_valid(self, match: Any) -> bool:
        return self.charactor_id in self.request.available_charactor_ids


class RerollDiceResponse(ResponseBase):
    name: Literal['RerollDiceResponse'] = 'RerollDiceResponse'
    request: RerollDiceRequest
    reroll_dice_ids: List[int]

    def is_valid(self, match: Any) -> bool:
        """
        if have duplicate dice ids, or dice ids out of range, return False.
        """
        return list_unique_range_right(
            self.reroll_dice_ids, minn = 0, maxn = len(self.request.colors))


class SwitchCharactorResponse(ResponseBase):
    name: Literal['SwitchCharactorResponse'] = 'SwitchCharactorResponse'
    request: SwitchCharactorRequest
    charactor_id: int
    cost_ids: List[int]

    def is_valid(self, match: Any) -> bool:
        """
        Charactor is in the candidate charactors.
        Cost matches the request.
        """
        if self.charactor_id not in self.request.candidate_charactor_ids:
            return False
        if not list_unique_range_right(
            self.cost_ids, minn = 0, maxn = len(self.request.dice_colors)
        ):
            return False
        cost_colors = [self.request.dice_colors[i] for i in self.cost_ids]
        return self.request.cost.is_valid(cost_colors, 0)


class ElementalTuningResponse(ResponseBase):
    name: Literal['ElementalTuningResponse'] = 'ElementalTuningResponse'
    request: ElementalTuningRequest
    cost_id: int
    card_id: int

    def is_valid(self, match: Any) -> bool:
        """
        Check whether the response is valid.
        """
        return (
            self.cost_id in self.request.dice_ids
            and self.card_id in self.request.card_ids
        )


class DeclareRoundEndResponse(ResponseBase):
    name: Literal['DeclareRoundEndResponse'] = 'DeclareRoundEndResponse'
    request: DeclareRoundEndRequest


class UseSkillResponse(ResponseBase):
    """
    Response for use skill. Currently not support choose skill target.
    """
    name: Literal['UseSkillResponse'] = 'UseSkillResponse'
    request: UseSkillRequest
    cost_ids: List[int]

    def is_valid(self, match: Any) -> bool:
        """
        Check whether the response is valid.
        """
        if not list_unique_range_right(
            self.cost_ids, minn = 0, maxn = len(self.request.dice_colors)
        ):
            return False
        cost_colors = [self.request.dice_colors[i] for i in self.cost_ids]
        return self.request.cost.is_valid(cost_colors, 
                                          self.request.cost.charge)


class UseCardResponse(ResponseBase):
    name: Literal['UseCardResponse'] = 'UseCardResponse'
    request: UseCardRequest
    cost_ids: List[int]
    target: CardActionTarget | None

    def is_valid(self, match: Any) -> bool:
        """
        Check whether the response is valid.
        """
        # dice color right
        if not list_unique_range_right(
            self.cost_ids, minn = 0, maxn = len(self.request.dice_colors)
        ):
            return False
        cost_colors = [self.request.dice_colors[i] for i in self.cost_ids]
        if not self.request.cost.is_valid(cost_colors, 
                                          self.request.cost.charge):
            return False
        # if has targets, response target should not be None
        if self.target is None and len(self.request.targets) > 0:
            return False
        # if response target is not None, it should be in targets
        if self.target is not None:
            if self.target not in self.request.targets:
                return False
        return True


Requests = (
    SwitchCardRequest | ChooseCharactorRequest | RerollDiceRequest
    | SwitchCharactorRequest | ElementalTuningRequest
    | DeclareRoundEndRequest | UseSkillRequest | UseCardRequest
)

Responses = (
    SwitchCardResponse | ChooseCharactorResponse | RerollDiceResponse
    | SwitchCharactorResponse | ElementalTuningResponse
    | DeclareRoundEndResponse | UseSkillResponse | UseCardResponse
)
