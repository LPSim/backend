"""
Event handlers to implement system controls and special rules 
"""
from typing import List, Literal
from .object_base import ObjectBase
from .struct import ObjectPosition
from .consts import ObjectPositionType, DieColor
from .event import (
    ReceiveDamageEventArguments,
    AfterMakeDamageEventArguments,
    CharactorDefeatedEventArguments,
    RoundEndEventArguments,
    DrawCardEventArguments,
)
from .action import (
    Actions,
    CharactorDefeatedAction,
    GenerateChooseCharactorRequestAction,
    DrawCardAction,
    RemoveCardAction
)
from .modifiable_values import InitialDiceColorValue, RerollValue
from .elemental_reaction import elemental_reaction_side_effect


class SystemEventHandlerBase(ObjectBase):
    """
    Base class of system event handlers. Its position should be SYSTEM.
    """

    position: ObjectPosition = ObjectPosition(
        player_id = -1,
        area = ObjectPositionType.SYSTEM
    )


class SystemEventHandler(SystemEventHandlerBase):

    version: Literal['3.3', '3.4'] = '3.4'

    def event_handler_DRAW_CARD(
            self, event: DrawCardEventArguments) -> List[Actions]:
        """
        After draw card, check whether max card number is exceeded.
        """
        player_id = event.action.player_id
        hand_size = event.hand_size
        max_hand_size = event.max_hand_size
        actions = []
        if hand_size > max_hand_size:
            for i in range(hand_size, max_hand_size, -1):
                # remove the last card in hand repeatedly until hand size
                # is less than max hand size
                actions.append(RemoveCardAction(
                    player_id = player_id,
                    card_id = i - 1,
                    card_position = 'HAND',
                    remove_type = 'BURNED'
                ))
        return actions

    def event_handler_RECEIVE_DAMAGE(
            self, event: ReceiveDamageEventArguments) -> List[Actions]:
        """
        After receive damage, generate side effects of elemental reaction.
        """
        reaction = event.elemental_reaction
        player_id = event.final_damage.target_position.player_id
        charactor_id = event.final_damage.target_position.charactor_id
        act = elemental_reaction_side_effect(
            reaction, player_id, charactor_id, 
            version = self.version
        )
        if act is not None:
            return [act]
        return []

    def event_handler_AFTER_MAKE_DAMAGE(
            self, event: AfterMakeDamageEventArguments) -> List[Actions]:
        """
        After damage made, check whether anyone has defeated.
        """
        actions: List[Actions] = []
        for pnum, [hps, lives] in enumerate(zip(event.charactor_hps, 
                                                event.charactor_alive)):
            for cnum, [hp, alive] in enumerate(zip(hps, lives)):
                if hp == 0 and alive:
                    actions.append(CharactorDefeatedAction(
                        player_id = pnum,
                        charactor_id = cnum,
                    ))
        return actions

    def event_handler_CHARACTOR_DEFEATED(
            self, event: CharactorDefeatedEventArguments) -> List[Actions]:
        """
        After charactor defeated, check whether need to switch charactor.
        """
        if event.need_switch:
            return [GenerateChooseCharactorRequestAction(
                player_id = event.action.player_id,
            )]
        return []

    def event_handler_ROUND_END(
            self, event: RoundEndEventArguments) -> List[Actions]:
        """
        After round end, draw card for each player.
        """
        actions: List[Actions] = []
        first = event.player_go_first
        initial_card_draw = event.initial_card_draw
        actions.append(DrawCardAction(
            player_id = first,
            number = initial_card_draw,
            draw_if_filtered_not_enough = True
        ))
        actions.append(DrawCardAction(
            player_id = 1 - first,
            number = initial_card_draw,
            draw_if_filtered_not_enough = True
        ))
        return actions


class OmnipotentGuideEventHandler(SystemEventHandlerBase):

    def value_modifier_INITIAL_DICE_COLOR(
            self, value: InitialDiceColorValue, 
            mode: Literal['REAL', 'TEST']) -> InitialDiceColorValue:
        """
        remove current dice color and add 100 omni dice color
        """
        value.dice_colors = [DieColor.OMNI] * 100
        return value

    def value_modifier_REROLL(
            self, value: RerollValue, 
            mode: Literal['REAL', 'TEST']) -> RerollValue:
        """
        reroll set to 0
        """
        value.value = 0
        return value


SystemEventHandlers = (
    SystemEventHandlerBase | SystemEventHandler | OmnipotentGuideEventHandler
)
