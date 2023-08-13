from utils import BaseModel
from typing import Literal, List, Any
from .consts import DieColor, ElementalReactionType, ElementType
from .action import (
    ActionTypes, 
    ActionBase,
    DrawCardAction,
    RestoreCardAction,
    RemoveCardAction,
    ChooseCharactorAction,
    CreateDiceAction,
    RemoveDiceAction,
    DeclareRoundEndAction,
    CombatActionAction,
    SwitchCharactorAction,
    MakeDamageAction,
    ChargeAction,
    CharactorDefeatedAction,
)
from .modifiable_values import DamageValue, FinalDamageValue


class EventArgumentsBase(BaseModel):
    """
    Base class of event arguments. event arguments are generated when new
    Action is triggered by events. It is a superset of Action arguments, and
    will record nesessary information about the event.

    If new cards need more information about the event (e.g. Chinju Forest
    need to know which player goes first, which is not needed before version
    3.7), the information can be added to the event arguments.

    self.match is passed to dig information for handlers,
    but it is not recommended to dig information from self.match directly,
    better to add a new attribute for a event when some information is used.
    Only use it when adding some information is very difficult.
    """
    type: Literal[ActionTypes.EMPTY] = ActionTypes.EMPTY
    action: ActionBase
    match: Any


class DrawCardEventArguments(EventArgumentsBase):
    """
    Event arguments for draw card event.
    """
    type: Literal[ActionTypes.DRAW_CARD] = ActionTypes.DRAW_CARD
    action: DrawCardAction
    hand_size: int
    max_hand_size: int


class RestoreCardEventArguments(EventArgumentsBase):
    """
    Event arguments for restore card event.
    """
    type: Literal[ActionTypes.RESTORE_CARD] = ActionTypes.RESTORE_CARD
    action: RestoreCardAction
    card_names: List[str]


class RemoveCardEventArguments(EventArgumentsBase):
    """
    Event arguments for remove card event.
    """
    type: Literal[ActionTypes.REMOVE_CARD] = ActionTypes.REMOVE_CARD
    action: RemoveCardAction
    card_name: str


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


class RoundPrepareEventArguments(EventArgumentsBase):
    """
    Event arguments for round prepare event. This event is triggered 
    by the system when a new round starts, so it does not have an action.

    Args:
        player_go_first (int): The ID of the player who goes first.
        round (int): The number of the round.
        dice_colors (List[List[DiceColor]]): The colors of the dice of each
            player.
    """
    type: Literal[ActionTypes.ROUND_PREPARE] = ActionTypes.ROUND_PREPARE
    action: ActionBase = ActionBase(type = ActionTypes.EMPTY)
    player_go_first: int
    round: int
    dice_colors: List[List[DieColor]]


class DeclareRoundEndEventArguments(EventArgumentsBase):
    """
    Event arguments for declare round end event. This event is triggered 
    by the system when a player declares the end of the round, so it does 
    not have an action.
    """
    type: Literal[ActionTypes.DECLARE_ROUND_END] = \
        ActionTypes.DECLARE_ROUND_END
    action: DeclareRoundEndAction


class CombatActionEventArguments(EventArgumentsBase):
    """
    Event arguments for combat action event.
    """
    type: Literal[ActionTypes.COMBAT_ACTION] = ActionTypes.COMBAT_ACTION
    action: CombatActionAction


class SwitchCharactorEventArguments(EventArgumentsBase):
    """
    Event arguments for switch charactor event.
    """
    type: Literal[ActionTypes.SWITCH_CHARACTOR] = ActionTypes.SWITCH_CHARACTOR
    action: SwitchCharactorAction
    last_active_charactor_id: int


class ReceiveDamageEventArguments(EventArgumentsBase):
    """
    Event arguments for receive damage event. Some objects may trigger events
    before charactor defeated settlement start when received special 
    damages, e.g. Seed of Skandha, Tenacity of the Millelith, Cryo Cicins.
    """
    type: Literal[ActionTypes.RECEIVE_DAMAGE] = ActionTypes.RECEIVE_DAMAGE
    action: MakeDamageAction
    original_damage: DamageValue
    final_damage: FinalDamageValue
    hp_before: int
    hp_after: int
    elemental_reaction: ElementalReactionType
    reacted_elements: List[ElementType]


class MakeDamageEventArguments(EventArgumentsBase):
    """
    Event arguments for make damage event. Some objects may trigger events
    before charactor defeated settlement start, e.g. reburn.
    """

    type: Literal[ActionTypes.MAKE_DAMAGE] = ActionTypes.MAKE_DAMAGE
    action: MakeDamageAction
    damages: List[ReceiveDamageEventArguments]
    charactor_hps: List[List[int]]
    charactor_alive: List[List[bool]]


class AfterMakeDamageEventArguments(MakeDamageEventArguments):
    """
    Event arguments for make damage event, contains character defeated
    settlements.
    """

    type: Literal[ActionTypes.AFTER_MAKE_DAMAGE] = \
        ActionTypes.AFTER_MAKE_DAMAGE
    action: MakeDamageAction
    damages: List[ReceiveDamageEventArguments]

    @staticmethod
    def from_make_damage_event_arguments(
        event_arguments: MakeDamageEventArguments
    ) -> 'AfterMakeDamageEventArguments':
        return AfterMakeDamageEventArguments(
            match = event_arguments.match,
            action = event_arguments.action,
            damages = event_arguments.damages,
            charactor_hps = event_arguments.charactor_hps,
            charactor_alive = event_arguments.charactor_alive
        )


class ChargeEventArguments(EventArgumentsBase):
    """
    Event arguments for charge event.
    """
    type: Literal[ActionTypes.CHARGE] = ActionTypes.CHARGE
    action: ChargeAction
    charge_before: int
    charge_after: int


class SkillEndEventArguments(EventArgumentsBase):
    """
    Event arguments for skill end event.
    """
    type: Literal[ActionTypes.SKILL_END] = ActionTypes.SKILL_END
    action: ActionBase = ActionBase(type = ActionTypes.EMPTY)


class CharactorDefeatedEventArguments(EventArgumentsBase):
    """
    Event arguments for charactor defeated event.
    """
    type: Literal[ActionTypes.CHARACTOR_DEFEATED] = \
        ActionTypes.CHARACTOR_DEFEATED
    action: CharactorDefeatedAction
    need_switch: bool


class RoundEndEventArguments(EventArgumentsBase):
    """
    Event arguments for round end event. This event is triggered 
    by the system when a round ends, so it does not have an action.

    Args:
        player_go_first (int): The ID of the player who goes first.
        round (int): The number of the round.
    """
    type: Literal[ActionTypes.ROUND_END] = ActionTypes.ROUND_END
    action: ActionBase = ActionBase(type = ActionTypes.EMPTY)
    player_go_first: int
    round: int
    initial_card_draw: int

# TODO: combine arguments of events and actions.
# interactions和event&action的参数独立，event是action超集包含了额外的信息，
# registry里用hook勾住某个event。同时
# 考虑偏序，hook要包含object的优先级。不同object判断项不同，例如个人status包含
# 玩家编号角色id等，而全局status只包含玩家编号。排序时考虑object类型，当前前台玩家，
# 当前出战角色。排序放在registry里，每次触发event时，registry会自动排序。
# action包含执行一个动作的信息，event则包含根据这个动作触发的事件所需要的信息，包括
# action本身的信息以及额外的信息，用于判断是否触发事件。
