from typing import Dict, List, Literal

from ....action import CreateObjectAction, SwitchCharacterAction

from .....utils.class_registry import register_class
from ....event import RoundEndEventArguments
from ....consts import IconType, ObjectPositionType
from ....status.character_status.base import CharacterStatusBase
from ....match import Match
from ....struct import Cost, ObjectPosition
from ....object_base import EventCardBase
from .....utils.desc_registry import DescDictType


class FlickeringFourLeafSigilStatus_4_3(CharacterStatusBase):
    name: Literal["Flickering Four-Leaf Sigil"] = "Flickering Four-Leaf Sigil"
    version: Literal["4.3"] = "4.3"
    usage: int = 0
    max_usage: int = 0
    icon_type: IconType = IconType.SPECIAL

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Match
    ) -> List[SwitchCharacterAction]:
        """
        At the end of every round, switch to this character.
        """
        current_active = match.player_tables[
            self.position.player_idx
        ].active_character_idx
        if current_active == self.position.character_idx:
            # already active, do nothing
            return []
        return [
            SwitchCharacterAction(
                player_idx=self.position.player_idx,
                character_idx=self.position.character_idx,
            )
        ]


class FlickeringFourLeafSigil_4_3(EventCardBase):
    name: Literal["Flickering Four-Leaf Sigil"]
    version: Literal["4.3"] = "4.3"
    cost: Cost = Cost()

    def get_targets(self, match: Match) -> List[ObjectPosition]:
        # all alive characters
        ret: List[ObjectPosition] = []
        characters = match.player_tables[self.position.player_idx].characters
        for character in characters:
            if character.is_alive:
                ret.append(character.position)
        return ret

    def get_actions(
        self, target: ObjectPosition | None, match: Match
    ) -> List[CreateObjectAction]:
        assert target is not None
        return [
            CreateObjectAction(
                object_name=self.name,
                object_position=target.set_area(ObjectPositionType.CHARACTER_STATUS),
                object_arguments={},
            )
        ]


desc: Dict[str, DescDictType] = {
    "CHARACTER_STATUS/Flickering Four-Leaf Sigil": {
        "names": {"en-US": "Flickering Four-Leaf Sigil", "zh-CN": "浮烁的四叶印"},
        "descs": {
            "4.3": {
                "en-US": "At the End Phase of Every Round, you will switch to this character.",  # noqa: E501
                "zh-CN": "每个回合的结束阶段，我方都切换到此角色。",
            }
        },
    },
    "CARD/Flickering Four-Leaf Sigil": {
        "names": {"en-US": "Flickering Four-Leaf Sigil", "zh-CN": "浮烁的四叶印"},
        "descs": {
            "4.3": {
                "en-US": "Attached Four-Leaf Sigil to target character: At the End Phase of Every Round, you will switch to this character.",  # noqa: E501
                "zh-CN": "目标角色附属四叶印：每个回合的结束阶段，我方都切换到此角色。",
            }
        },
        "image_path": "cardface/Event_Event_Siyeyin.png",  # noqa: E501
        "id": 332027,
    },
}


register_class(FlickeringFourLeafSigil_4_3 | FlickeringFourLeafSigilStatus_4_3, desc)
