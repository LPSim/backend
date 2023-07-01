from utils import BaseModel
from typing import Literal, List
from .consts import DieColor
from .action import (
    Actions, 
    ActionTypes, 
    DrawCardAction,
    RestoreCardAction,
    ChooseCharactorAction,
    CreateDiceAction,
    RemoveDiceAction,
)


class EventArgumentsBase(BaseModel):
    """
    Base class of event arguments. event arguments are generated when new
    Action is triggered by events. It is a superset of Action arguments, and
    will record nesessary information about the event.

    If new cards need more information about the event (e.g. Chinju Forest
    need to know which player goes first, which is not needed before version
    3.7), the information can be added to the event arguments.
    """
    type: Literal[ActionTypes.EMPTY] = ActionTypes.EMPTY
    action: Actions


class DrawCardEventArguments(EventArgumentsBase):
    """
    Event arguments for draw card event.
    """
    type: Literal[ActionTypes.DRAW_CARD] = ActionTypes.DRAW_CARD
    action: DrawCardAction


class RestoreCardEventArguments(EventArgumentsBase):
    """
    Event arguments for restore card event.
    """
    type: Literal[ActionTypes.RESTORE_CARD] = ActionTypes.RESTORE_CARD
    action: RestoreCardAction
    card_names: List[str]


class ChooseCharactorEventArguments(EventArgumentsBase):
    """
    Event arguments for choose charactor event.
    """
    type: Literal[
        ActionTypes.CHOOSE_CHARACTOR] = ActionTypes.CHOOSE_CHARACTOR
    action: ChooseCharactorAction
    original_charactor_id: int


class CreateDiceEventArguments(EventArgumentsBase):
    """
    Event arguments for create dice event.

    Args:
        colors_generated (List[DieColor]): The colors of the dice
            generated.
        colors_over_maximum (List[DieColor]): The colors of the dice
            that are over the maximum number of dice and not obtained.
    """
    type: Literal[ActionTypes.CREATE_DICE] = ActionTypes.CREATE_DICE
    action: CreateDiceAction
    colors_generated: List[DieColor]
    colors_over_maximum: List[DieColor]


class RemoveDiceEventArguments(EventArgumentsBase):
    """
    Event arguments for remove dice event.

    Args:
        colors_removed (List[DieColor]): The colors of the dice.
    """
    type: Literal[ActionTypes.REMOVE_DICE] = ActionTypes.REMOVE_DICE
    action: RemoveDiceAction
    colors_removed: List[DieColor]


EventArguments = EventArgumentsBase | DrawCardEventArguments

# TODO: combine arguments of events and actions.
# interactions和event&action的参数独立，event是action超集包含了额外的信息，
# registry里用hook勾住某个event。同时
# 考虑偏序，hook要包含object的优先级。不同object判断项不同，例如个人buff包含
# 玩家编号角色id等，而全局buff只包含玩家编号。排序时考虑object类型，当前前台玩家，
# 当前出战角色。排序放在registry里，每次触发event时，registry会自动排序。
# action包含执行一个动作的信息，event则包含根据这个动作触发的事件所需要的信息，包括
# action本身的信息以及额外的信息，用于判断是否触发事件。
