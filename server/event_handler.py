"""
Event handlers to implement system controls and special rules 
"""
from typing import List
from .object_base import ObjectBase
from .event import (
    AfterMakeDamageEventArguments,
    CharactorDefeatedEventArguments,
)
from .action import (
    Actions,
    CharactorDefeatedAction,
    GenerateChooseCharactorRequestAction,
)


class SystemEventHandler(ObjectBase):

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
