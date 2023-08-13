"""
Event handlers to implement system controls and special rules 
"""
from typing import List
from .object_base import ObjectBase
from .event import (
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


class SystemEventHandler(ObjectBase):

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
            number = initial_card_draw
        ))
        actions.append(DrawCardAction(
            player_id = 1 - first,
            number = initial_card_draw
        ))
        return actions
