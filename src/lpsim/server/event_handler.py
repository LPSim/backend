"""
Event handlers to implement system controls and special rules 
"""
from typing import Dict, List, Literal, Any

from ..utils.desc_registry import DescDictType

from ..utils.class_registry import register_base_class, register_class
from .object_base import ObjectBase
from .struct import ObjectPosition
from .consts import ObjectPositionType, DieColor, ObjectType
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

    name: Literal['SystemEventHandlerBase']
    type: Literal[ObjectType.SYSTEM] = ObjectType.SYSTEM

    position: ObjectPosition = ObjectPosition(
        player_idx = -1,
        area = ObjectPositionType.SYSTEM,
        id = -1,
    )

    def renew(
        self, target: 'SystemEventHandlerBase'
    ) -> None:  # pragma: no cover
        """
        No need to renew.
        """
        pass


register_base_class(SystemEventHandlerBase)


class SystemEventHandler_3_3(SystemEventHandlerBase):

    name: Literal['System'] = 'System'
    version: Literal['3.3'] = '3.3'

    def event_handler_DRAW_CARD(
            self, event: DrawCardEventArguments, match: Any) -> List[Actions]:
        """
        After draw card, check whether max card number is exceeded.
        """
        player_idx = event.action.player_idx
        hand_size = event.hand_size
        max_hand_size = event.max_hand_size
        actions = []
        hands = match.player_tables[player_idx].hands
        if hand_size > max_hand_size:
            for i in range(hand_size, max_hand_size, -1):
                # remove the last card in hand repeatedly until hand size
                # is less than max hand size
                actions.append(RemoveCardAction(
                    position = hands[i - 1].position,
                    remove_type = 'BURNED'
                ))
        return actions

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Any
    ) -> List[Actions]:
        """
        After receive damage, generate side effects of elemental reaction.
        """
        reaction = event.elemental_reaction
        player_idx = event.final_damage.target_position.player_idx
        charactor_idx = event.final_damage.target_position.charactor_idx
        act = elemental_reaction_side_effect(
            reaction, player_idx, charactor_idx, 
            version = self.version
        )
        if act is not None:
            return [act]
        return []

    def event_handler_AFTER_MAKE_DAMAGE(
        self, event: AfterMakeDamageEventArguments, match: Any
    ) -> List[Actions]:
        """
        After damage made, check whether anyone has defeated.
        """
        actions: List[Actions] = []
        for pnum, table in enumerate(match.player_tables):
            for cnum, charactor in enumerate(table.charactors):
                if charactor.hp == 0 and charactor.is_alive:
                    charactor.is_alive = False  # mark as defeated first
                    actions.append(CharactorDefeatedAction(
                        player_idx = pnum,
                        charactor_idx = cnum,
                    ))
        return actions

    def event_handler_CHARACTOR_DEFEATED(
        self, event: CharactorDefeatedEventArguments, match: Any
    ) -> List[Actions]:
        """
        After charactor defeated, check whether need to switch charactor.
        """
        if event.need_switch:
            return [GenerateChooseCharactorRequestAction(
                player_idx = event.action.player_idx,
            )]
        return []

    def event_handler_ROUND_END(
            self, event: RoundEndEventArguments, match: Any) -> List[Actions]:
        """
        After round end, draw card for each player.
        """
        actions: List[Actions] = []
        first = event.player_go_first
        initial_card_draw = event.initial_card_draw
        actions.append(DrawCardAction(
            player_idx = first,
            number = initial_card_draw,
            draw_if_filtered_not_enough = True
        ))
        actions.append(DrawCardAction(
            player_idx = 1 - first,
            number = initial_card_draw,
            draw_if_filtered_not_enough = True
        ))
        return actions


class SystemEventHandler_3_4(SystemEventHandler_3_3):
    version: Literal['3.4'] = '3.4'


class OmnipotentGuideEventHandler_3_3(SystemEventHandlerBase):

    name: Literal['Omnipotent Guide'] = 'Omnipotent Guide'
    version: Literal['3.3'] = '3.3'

    def value_modifier_INITIAL_DICE_COLOR(
            self, value: InitialDiceColorValue, 
            match: Any,
            mode: Literal['REAL', 'TEST']) -> InitialDiceColorValue:
        """
        remove current dice color and add 100 omni dice color
        """
        value.dice_colors = [DieColor.OMNI] * 100
        return value

    def value_modifier_REROLL(
            self, value: RerollValue, 
            match: Any,
            mode: Literal['REAL', 'TEST']) -> RerollValue:
        """
        reroll set to 0
        """
        value.value = 0
        return value


SystemEventHandler = SystemEventHandler_3_4


event_handler_descs: Dict[str, DescDictType] = {
    "SYSTEM/System": {
        "names": {
            "zh-CN": "系统事件",
            "en-US": "System events"
        },
        "descs": {
            "3.3": {
            },
            "3.4": {
            }
        }
    },
    "SYSTEM/Omnipotent Guide": {
        "names": {
            "zh-CN": "万能向导",
            "en-US": "Omnipotent Guide"
        },
        "descs": {
            "3.3": {
            }
        }
    },
}


register_class(
    SystemEventHandler_3_3 | OmnipotentGuideEventHandler_3_3 
    | SystemEventHandler_3_4,
    event_handler_descs
)
