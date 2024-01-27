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
    AfterMakeDamageEventArguments,
    CharacterDefeatedEventArguments,
    RoundEndEventArguments,
    DrawCardEventArguments,
    RoundPrepareEventArguments,
    SkillEndEventArguments,
)
from .action import (
    Actions,
    CharacterDefeatedAction,
    GenerateChooseCharacterRequestAction,
    DrawCardAction,
    RemoveCardAction,
)
from .modifiable_values import InitialDiceColorValue, RerollValue


class SystemEventHandlerBase(ObjectBase):
    """
    Base class of system event handlers. Its position should be SYSTEM.
    """

    name: Literal["SystemEventHandlerBase"]
    type: Literal[ObjectType.SYSTEM] = ObjectType.SYSTEM

    position: ObjectPosition = ObjectPosition(
        player_idx=-1,
        area=ObjectPositionType.SYSTEM,
        id=-1,
    )

    def renew(self, target: "SystemEventHandlerBase") -> None:  # pragma: no cover
        """
        No need to renew.
        """
        pass


register_base_class(SystemEventHandlerBase)


class SystemEventHandler_3_3(SystemEventHandlerBase):
    name: Literal["System"] = "System"
    version: Literal["3.3"] = "3.3"

    def event_handler_DRAW_CARD(
        self, event: DrawCardEventArguments, match: Any
    ) -> List[Actions]:
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
                actions.append(
                    RemoveCardAction(
                        position=hands[i - 1].position, remove_type="BURNED"
                    )
                )
        return actions

    def event_handler_AFTER_MAKE_DAMAGE(
        self, event: AfterMakeDamageEventArguments, match: Any
    ) -> List[Actions]:
        """
        After damage made, check whether anyone has defeated.
        """
        actions: List[Actions] = []
        for pnum, table in enumerate(match.player_tables):
            for cnum, character in enumerate(table.characters):
                if character.hp == 0 and character.is_alive:
                    character.is_alive = False  # mark as defeated first
                    actions.append(
                        CharacterDefeatedAction(
                            player_idx=pnum,
                            character_idx=cnum,
                        )
                    )
        return actions

    def event_handler_CHARACTER_DEFEATED(
        self, event: CharacterDefeatedEventArguments, match: Any
    ) -> List[Actions]:
        """
        After character defeated, check whether need to switch character.
        """
        if event.need_switch:
            return [
                GenerateChooseCharacterRequestAction(
                    player_idx=event.action.player_idx,
                )
            ]
        return []

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[Actions]:
        """
        After round end, draw card for each player.
        """
        actions: List[Actions] = []
        first = event.player_go_first
        initial_card_draw = event.initial_card_draw
        actions.append(
            DrawCardAction(
                player_idx=first,
                number=initial_card_draw,
                draw_if_filtered_not_enough=True,
            )
        )
        actions.append(
            DrawCardAction(
                player_idx=1 - first,
                number=initial_card_draw,
                draw_if_filtered_not_enough=True,
            )
        )
        return actions


class SystemEventHandler_3_4(SystemEventHandler_3_3):
    version: Literal["3.4"] = "3.4"


class OmnipotentGuideEventHandler_3_3(SystemEventHandlerBase):
    name: Literal["Omnipotent Guide"] = "Omnipotent Guide"
    version: Literal["3.3"] = "3.3"

    def value_modifier_INITIAL_DICE_COLOR(
        self, value: InitialDiceColorValue, match: Any, mode: Literal["REAL", "TEST"]
    ) -> InitialDiceColorValue:
        """
        remove current dice color and add 100 omni dice color
        """
        value.dice_colors = [DieColor.OMNI] * 100
        return value

    def value_modifier_REROLL(
        self, value: RerollValue, match: Any, mode: Literal["REAL", "TEST"]
    ) -> RerollValue:
        """
        reroll set to 0
        """
        value.value = 0
        return value


class EllinEventHandler_3_3(SystemEventHandlerBase):
    """
    This handler will record all skill ids used in this round.
    """

    name: Literal["Ellin"] = "Ellin"
    version: Literal["3.3"] = "3.3"
    recorded_skill_ids: Dict[int, None] = {}

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        self.recorded_skill_ids.clear()
        return []

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[Actions]:
        """
        Record skill id when skill end.
        """
        self.recorded_skill_ids[event.action.position.id] = None
        return []


class IHaventLostYetEventHandler_3_3(SystemEventHandlerBase):
    """
    This handler will record whether anyone is defeated this round for each
    player.
    """

    name: Literal["I Haven't Lost Yet!"] = "I Haven't Lost Yet!"
    version: Literal["3.3"] = "3.3"
    defeated: List[bool] = [False, False]

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        self.defeated = [False, False]
        return []

    def event_handler_CHARACTER_DEFEATED(
        self, event: CharacterDefeatedEventArguments, match: Any
    ) -> List[Actions]:
        self.defeated[event.action.player_idx] = True
        return []


SystemEventHandler = SystemEventHandler_3_4


event_handler_descs: Dict[str, DescDictType] = {
    "SYSTEM/System": {
        "names": {"zh-CN": "系统事件", "en-US": "System events"},
        "descs": {"3.3": {}, "3.4": {}},
    },
    "SYSTEM/Omnipotent Guide": {
        "names": {"zh-CN": "万能向导", "en-US": "Omnipotent Guide"},
        "descs": {"3.3": {}},
    },
    "SYSTEM/Ellin": {
        "names": {"zh-CN": "艾琳", "en-US": "Ellin"},
        "descs": {"3.3": {}},
    },
    "SYSTEM/I Haven't Lost Yet!": {
        "names": {"zh-CN": "本大爷还没有输！", "en-US": "I Haven't Lost Yet!"},
        "descs": {"3.3": {}},
    },
}


register_class(
    SystemEventHandler_3_3
    | OmnipotentGuideEventHandler_3_3
    | SystemEventHandler_3_4
    | EllinEventHandler_3_3
    | IHaventLostYetEventHandler_3_3,
    event_handler_descs,
)
