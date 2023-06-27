from utils import BaseModel
from typing import Literal, List
from .action import (
    Actions, 
    ActionTypes, 
    DrawCardAction,
    RestoreCardAction,
    ChooseCharactorAction,
)


class EventArgumentsBase(BaseModel):
    """
    Base class of event arguments. event arguments are generated when new
    Action is triggered by events. It is a superset of Action arguments, and
    will record nesessary information about the event.
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


EventArguments = EventArgumentsBase | DrawCardEventArguments

# TODO: combine arguments of events and actions.
# interactions和event&action的参数独立，event是action超集包含了额外的信息，
# registry里用hook勾住某个event。同时
# 考虑偏序，hook要包含object的优先级。不同object判断项不同，例如个人buff包含
# 玩家编号角色id等，而全局buff只包含玩家编号。排序时考虑object类型，当前前台玩家，
# 当前出战角色。排序放在registry里，每次触发event时，registry会自动排序。
# action包含执行一个动作的信息，event则包含根据这个动作触发的事件所需要的信息，包括
# action本身的信息以及额外的信息，用于判断是否触发事件。
