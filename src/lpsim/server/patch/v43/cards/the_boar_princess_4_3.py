from typing import Dict, List, Literal

from .....utils.class_registry import register_class

from ....status.team_status.base import RoundTeamStatus

from ....consts import DieColor, IconType, ObjectPositionType, ObjectType
from ....action import CreateDiceAction, CreateObjectAction, RemoveObjectAction
from ....match import Match
from ....event import RemoveObjectEventArguments, RoundPrepareEventArguments
from ....struct import Cost, ObjectPosition
from ....object_base import EventCardBase
from .....utils.desc_registry import DescDictType


class TheBoarPrincessStatus_4_3(RoundTeamStatus):
    name: Literal["The Boar Princess"] = "The Boar Princess"
    version: Literal["4.3"] = "4.3"
    usage: int = 2
    max_usage: int = 2
    icon_type: IconType = IconType.BUFF

    def event_handler_REMOVE_OBJECT(
        self, event: RemoveObjectEventArguments, match: Match
    ) -> List[CreateDiceAction | RemoveObjectAction]:
        """
        When self equipment removed from character, create one omni die
        """
        position = event.action.object_position
        if position.player_idx != self.position.player_idx:
            # not self
            return []
        if position.area != ObjectPositionType.CHARACTER:
            # not remove character objects, i.e. equipment
            return []
        if event.object_type == ObjectType.TALENT:
            # is talent, it should be removed because of character defeated.
            character = match.player_tables[position.player_idx].characters[
                position.character_idx
            ]
            if character.is_alive:
                # character is still alive, it should be because of
                # talent overwritten.
                return []
        assert self.usage > 0
        self.usage -= 1
        return [
            CreateDiceAction(
                player_idx=self.position.player_idx, number=1, color=DieColor.OMNI
            )
        ] + self.check_should_remove()

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Match
    ) -> List[RemoveObjectAction]:
        self.usage = 0
        return self.check_should_remove()


class TheBoarPrincess_4_3(EventCardBase):
    name: Literal["The Boar Princess"]
    version: Literal["4.3"] = "4.3"
    cost: Cost = Cost()

    def get_targets(self, match: Match) -> List[ObjectPosition]:
        # no target
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Match
    ) -> List[CreateObjectAction]:
        assert target is None
        return [
            CreateObjectAction(
                object_name=self.name,
                object_position=ObjectPosition(
                    player_idx=self.position.player_idx,
                    area=ObjectPositionType.TEAM_STATUS,
                    id=-1,
                ),
                object_arguments={},
            )
        ]


desc: Dict[str, DescDictType] = {
    "TEAM_STATUS/The Boar Princess": {
        "names": {"en-US": "The Boar Princess", "zh-CN": "野猪公主"},
        "descs": {
            "4.3": {
                "en-US": "Each time you discard an Equipment Card from one of your characters during this Round: Gain 1 Omni Element. (Max 2)\n(This effect can be triggered by the loss of an Equipment Card from a character falling or from having their Weapon or Artifact overwritten.)",  # noqa: E501
                "zh-CN": "本回合中，我方每有一张装备在角色身上的「装备牌」被弃置时：获得1个万能元素。（最多获得2个）\n（角色被击倒时弃置装备牌，或者覆盖装备「武器」或「圣遗物」，都可以触发此效果）",  # noqa: E501
            }
        },
    },
    "CARD/The Boar Princess": {
        "names": {"en-US": "The Boar Princess", "zh-CN": "野猪公主"},
        "descs": {
            "4.3": {
                "en-US": "Each time you discard an Equipment Card from one of your characters during this Round: Gain 1 Omni Element. (Max 2)\n(This effect can be triggered by the loss of an Equipment Card from a character falling or from having their Weapon or Artifact overwritten.)",  # noqa: E501
                "zh-CN": "本回合中，我方每有一张装备在角色身上的「装备牌」被弃置时：获得1个万能元素。（最多获得2个）\n（角色被击倒时弃置装备牌，或者覆盖装备「武器」或「圣遗物」，都可以触发此效果）",  # noqa: E501
            }
        },
        "image_path": "cardface/Event_Event_Yezhu.png",  # noqa: E501
        "id": 332025,
    },
}


register_class(TheBoarPrincess_4_3 | TheBoarPrincessStatus_4_3, desc)
