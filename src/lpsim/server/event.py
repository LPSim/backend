from .struct import ObjectPosition
from ..utils import BaseModel
from typing import Any, Literal, List
from .consts import DieColor, ElementalReactionType, ElementType
from .action import (
    ActionTypes, 
    ActionBase,
    Actions,
    DrawCardAction,
    RestoreCardAction,
    RemoveCardAction,
    ChooseCharactorAction,
    CreateDiceAction,
    RemoveDiceAction,
    DeclareRoundEndAction,
    ActionEndAction,
    SkillEndAction,
    SwitchCharactorAction,
    MakeDamageAction,
    ChargeAction,
    CharactorDefeatedAction,
    CreateObjectAction,
    RemoveObjectAction,
    ChangeObjectUsageAction,
    MoveObjectAction,
    ConsumeArcaneLegendAction,
    UseCardAction,
    UseSkillAction,
    CharactorReviveAction
)
from .modifiable_values import DamageValue, FinalDamageValue


class EventArgumentsBase(BaseModel):
    """
    Base class of event arguments. event arguments are generated when new
    Action is triggered by events. It is a superset of Action arguments, and
    will record nesessary information about the event.
    """
    type: Literal[ActionTypes.EMPTY] = ActionTypes.EMPTY
    action: ActionBase


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
    original_charactor_idx: int


# 5


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


class GameStartEventArguments(EventArgumentsBase):
    """
    Event arguments for game start event. This event is triggered 
    by the system when the game starts, so it does not have an action.

    Args:
        player_go_first (int): The index of the player who goes first.
    """
    type: Literal[ActionTypes.GAME_START] = ActionTypes.GAME_START
    action: ActionBase = ActionBase(type = ActionTypes.EMPTY)
    player_go_first: int


class RoundPrepareEventArguments(EventArgumentsBase):
    """
    Event arguments for round prepare event. This event is triggered 
    by the system when a new round starts, so it does not have an action.

    Args:
        player_go_first (int): The index of the player who goes first.
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


# 10


class ActionEndEventArguments(EventArgumentsBase):
    """
    Event arguments for action end event.
    """
    type: Literal[ActionTypes.ACTION_END] = ActionTypes.ACTION_END
    action: ActionEndAction
    do_combat_action: bool


class SwitchCharactorEventArguments(EventArgumentsBase):
    """
    Event arguments for switch charactor event.
    """
    type: Literal[ActionTypes.SWITCH_CHARACTOR] = ActionTypes.SWITCH_CHARACTOR
    action: SwitchCharactorAction
    last_active_charactor_idx: int


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
            action = event_arguments.action,
            damages = event_arguments.damages,
        )


# 15


class ChargeEventArguments(EventArgumentsBase):
    """
    Event arguments for charge event.
    """
    type: Literal[ActionTypes.CHARGE] = ActionTypes.CHARGE
    action: ChargeAction
    charge_before: int
    charge_after: int


class UseSkillEventArguments(EventArgumentsBase):
    """
    Event arguments for use skill.
    """
    type: Literal[ActionTypes.USE_SKILL] = ActionTypes.USE_SKILL
    action: UseSkillAction


class SkillEndEventArguments(EventArgumentsBase):
    """
    Event arguments for skill end event.
    """
    type: Literal[ActionTypes.SKILL_END] = ActionTypes.SKILL_END
    action: SkillEndAction


class CharactorDefeatedEventArguments(EventArgumentsBase):
    """
    Event arguments for charactor defeated event.
    """
    type: Literal[ActionTypes.CHARACTOR_DEFEATED] = \
        ActionTypes.CHARACTOR_DEFEATED
    action: CharactorDefeatedAction
    need_switch: bool


class CreateObjectEventArguments(EventArgumentsBase):
    """
    Event arguments for create object event.
    """
    type: Literal[ActionTypes.CREATE_OBJECT] = ActionTypes.CREATE_OBJECT
    action: CreateObjectAction
    create_result: Literal['NEW', 'RENEW']
    create_idx: int


# 20


class RemoveObjectEventArguments(EventArgumentsBase):
    """
    Event arguments for remove object event.
    """
    type: Literal[ActionTypes.REMOVE_OBJECT] = ActionTypes.REMOVE_OBJECT
    action: RemoveObjectAction
    object_name: str


class ChangeObjectUsageEventArguments(EventArgumentsBase):
    """
    Event arguments for change object usage event.
    """
    type: Literal[ActionTypes.CHANGE_OBJECT_USAGE] = \
        ActionTypes.CHANGE_OBJECT_USAGE
    action: ChangeObjectUsageAction
    object_name: str
    usage_before: int
    usage_after: int


class MoveObjectEventArguments(EventArgumentsBase):
    """
    Event arguments for move object event.
    """
    type: Literal[ActionTypes.MOVE_OBJECT] = ActionTypes.MOVE_OBJECT
    action: MoveObjectAction
    object_name: str


class ConsumeArcaneLegendEventArguments(EventArgumentsBase):
    """
    Event arguments for consume arcane legend event.
    """
    type: Literal[ActionTypes.CONSUME_ARCANE_LEGEND] = \
        ActionTypes.CONSUME_ARCANE_LEGEND
    action: ConsumeArcaneLegendAction


class RoundEndEventArguments(EventArgumentsBase):
    """
    Event arguments for round end event. This event is triggered 
    by the system when a round ends, so it does not have an action.

    Args:
        player_go_first (int): The index of the player who goes first.
        round (int): The number of the round.
    """
    type: Literal[ActionTypes.ROUND_END] = ActionTypes.ROUND_END
    action: ActionBase = ActionBase(type = ActionTypes.EMPTY)
    player_go_first: int
    round: int
    initial_card_draw: int


# 25


class PlayerActionStartEventArguments(EventArgumentsBase):
    """
    Event arguments for action start event.
    """
    type: Literal[ActionTypes.PLAYER_ACTION_START] = \
        ActionTypes.PLAYER_ACTION_START
    action: ActionBase = ActionBase(type = ActionTypes.EMPTY)
    player_idx: int


class CharactorReviveEventArguments(EventArgumentsBase):
    """
    Event arguments for charactor revive event.
    """
    type: Literal[ActionTypes.CHARACTOR_REVIVE] = \
        ActionTypes.CHARACTOR_REVIVE
    action: CharactorReviveAction


class UseCardEventArguments(EventArgumentsBase):
    """
    Event arguments for use card event.
    """
    type: Literal[ActionTypes.USE_CARD] = ActionTypes.USE_CARD
    action: UseCardAction
    card: Any


EventArguments = (
    EventArgumentsBase
    | DrawCardEventArguments
    | RestoreCardEventArguments
    | RemoveCardEventArguments
    | ChooseCharactorEventArguments
    # 5
    | CreateDiceEventArguments
    | RemoveDiceEventArguments
    | GameStartEventArguments
    | RoundPrepareEventArguments
    | DeclareRoundEndEventArguments
    # 10
    | ActionEndEventArguments
    | SwitchCharactorEventArguments
    | ReceiveDamageEventArguments
    | MakeDamageEventArguments
    | AfterMakeDamageEventArguments
    # 15
    | ChargeEventArguments
    | UseSkillEventArguments
    | SkillEndEventArguments
    | CharactorDefeatedEventArguments
    | CreateObjectEventArguments
    # 20
    | RemoveObjectEventArguments
    | ChangeObjectUsageEventArguments
    | MoveObjectEventArguments
    | ConsumeArcaneLegendEventArguments
    | RoundEndEventArguments
    # 25
    | PlayerActionStartEventArguments
    | CharactorReviveEventArguments
    | UseCardEventArguments
)


class EventFrame(BaseModel):
    """
    Event frame is a frame of events, contains events with their arguments, the
    object lists that will be triggered by the event arguments, and the
    action lists that has triggered.

    When one action is done, it will generate a new event frame, with various
    number of events, and append it to the event frame list. When there are
    events and no processing objects and actions, the first event will 
    trigger objects. When there are triggered objects, the first object 
    position will be popped and trigger actions. When there are triggered
    actions, the first action will be popped and trigger events, then add
    a new event frame. If an event frame has no events, no triggered objects
    and no triggered actions, it will be removed from the list.
    """
    events: List[EventArguments]
    processing_event: EventArguments | None = None
    triggered_objects: List[ObjectPosition] = []
    triggered_actions: List[Actions] = []
