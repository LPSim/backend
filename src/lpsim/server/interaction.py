from ..utils import BaseModel, list_unique_range_right
from typing import Literal, List, Any
from .consts import DieColor
from .struct import Cost, MultipleObjectPosition, ObjectPosition


class RequestBase(BaseModel):
    """
    Base class of request.
    """
    name: Literal['RequestBase'] = 'RequestBase'
    player_idx: int


class SwitchCardRequest(RequestBase):
    name: Literal['SwitchCardRequest'] = 'SwitchCardRequest'
    card_names: List[str]
    maximum_switch_number: int = 999


class ChooseCharactorRequest(RequestBase):
    name: Literal['ChooseCharactorRequest'] = 'ChooseCharactorRequest'
    available_charactor_idxs: List[int]


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
    active_charactor_idx: int
    target_charactor_idx: int
    dice_colors: List[DieColor]
    cost: Cost


class ElementalTuningRequest(RequestBase):
    """
    Request for elemental tuning.
    """
    name: Literal['ElementalTuningRequest'] = 'ElementalTuningRequest'
    dice_colors: List[DieColor]
    dice_idxs: List[int]
    card_idxs: List[int]


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
    charactor_idx: int
    skill_idx: int
    dice_colors: List[DieColor]
    cost: Cost


class UseCardRequest(RequestBase):
    """
    Request for use card.
    """
    name: Literal['UseCardRequest'] = 'UseCardRequest'
    card_idx: int
    dice_colors: List[DieColor]
    targets: List[ObjectPosition | MultipleObjectPosition]
    cost: Cost


class ResponseBase(BaseModel):
    """
    Base class of response.
    """
    name: Literal['ResponseBase'] = 'ResponseBase'
    request: RequestBase

    @property
    def player_idx(self) -> int:
        """
        Return the player idx of the response.
        """
        return self.request.player_idx

    def is_valid(self, match: Any) -> bool:
        """
        Check whether the response is valid.
        """
        return True


class SwitchCardResponse(ResponseBase):
    """
    Card indices want to switch, based on the request.
    """
    name: Literal['SwitchCardResponse'] = 'SwitchCardResponse'
    request: SwitchCardRequest
    card_idxs: List[int]

    def is_valid(self, match: Any) -> bool:
        if len(self.card_idxs) > self.request.maximum_switch_number:
            return False
        return list_unique_range_right(
            self.card_idxs, minn = 0, maxn = len(self.request.card_names))

    @property
    def card_names(self) -> List[str]:
        """
        Return the card names of the response.
        """
        return [self.request.card_names[i] for i in self.card_idxs]


class ChooseCharactorResponse(ResponseBase):
    name: Literal['ChooseCharactorResponse'] = 'ChooseCharactorResponse'
    request: ChooseCharactorRequest
    charactor_idx: int

    def is_valid(self, match: Any) -> bool:
        return self.charactor_idx in self.request.available_charactor_idxs


class RerollDiceResponse(ResponseBase):
    name: Literal['RerollDiceResponse'] = 'RerollDiceResponse'
    request: RerollDiceRequest
    reroll_dice_idxs: List[int]

    def is_valid(self, match: Any) -> bool:
        """
        if have duplicate dice indices, or dice indices out of range, 
        return False.
        """
        return list_unique_range_right(
            self.reroll_dice_idxs, minn = 0, maxn = len(self.request.colors))


class SwitchCharactorResponse(ResponseBase):
    name: Literal['SwitchCharactorResponse'] = 'SwitchCharactorResponse'
    request: SwitchCharactorRequest
    dice_idxs: List[int]

    def is_valid(self, match: Any) -> bool:
        """
        Cost matches the request.
        """
        if not list_unique_range_right(
            self.dice_idxs, minn = 0, maxn = len(self.request.dice_colors)
        ):
            return False
        cost_colors = [self.request.dice_colors[i] for i in self.dice_idxs]
        return self.request.cost.is_valid(cost_colors, 0, False)


class ElementalTuningResponse(ResponseBase):
    name: Literal['ElementalTuningResponse'] = 'ElementalTuningResponse'
    request: ElementalTuningRequest
    dice_idx: int
    card_idx: int

    def is_valid(self, match: Any) -> bool:
        """
        Check whether the response is valid.
        """
        return (
            self.dice_idx in self.request.dice_idxs
            and self.card_idx in self.request.card_idxs
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
    dice_idxs: List[int]

    def is_valid(self, match: Any) -> bool:
        """
        Check whether the response is valid.
        """
        if not list_unique_range_right(
            self.dice_idxs, minn = 0, maxn = len(self.request.dice_colors)
        ):
            return False
        cost_colors = [self.request.dice_colors[i] for i in self.dice_idxs]
        table = match.player_tables[self.request.player_idx]
        charge, arcane_legend = table.get_charge_and_arcane_legend()
        return self.request.cost.is_valid(cost_colors, charge, arcane_legend)


class UseCardResponse(ResponseBase):
    name: Literal['UseCardResponse'] = 'UseCardResponse'
    request: UseCardRequest
    dice_idxs: List[int]
    target: ObjectPosition | MultipleObjectPosition | None

    def is_valid(self, match: Any) -> bool:
        """
        Check whether the response is valid.
        """
        # dice color right
        if not list_unique_range_right(
            self.dice_idxs, minn = 0, maxn = len(self.request.dice_colors)
        ):
            return False
        cost_colors = [self.request.dice_colors[i] for i in self.dice_idxs]
        table = match.player_tables[self.request.player_idx]
        charge, arcane_legend = table.get_charge_and_arcane_legend()
        if not self.request.cost.is_valid(cost_colors, charge, arcane_legend):
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
