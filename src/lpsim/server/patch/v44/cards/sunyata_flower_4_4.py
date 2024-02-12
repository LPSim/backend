from typing import Any, Dict, List, Literal, Type
from pydantic import PrivateAttr

from ....action import ActionTypes, Actions, CreateObjectAction, RemoveObjectAction
from .....utils.class_registry import get_instance, register_class
from ....event import GameStartEventArguments, MoveObjectEventArguments
from ....modifiable_values import CostValue
from ....status.team_status.base import RoundTeamStatus, UsageTeamStatus
from ....consts import CostLabels, IconType, ObjectPositionType
from .....utils.class_registry import get_class_list_by_base_class
from ....card.support.base import SupportBase
from ....struct import Cost, ObjectPosition
from ....match import Match
from ....object_base import EventCardBase
from .....utils.desc_registry import DescDictType


class SunyataFlowerStatus_4_4(UsageTeamStatus, RoundTeamStatus):
    name: Literal["Sunyata Flower"] = "Sunyata Flower"
    version: Literal["4.4"] = "4.4"
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.BUFF] = IconType.BUFF
    target_label: int = CostLabels.SUPPORTS.value

    def value_modifier_COST(
        self, value: CostValue, match: Match, mode: Literal["TEST", "REAL"]
    ) -> CostValue:
        """
        decrease weapons or artifact cost by 1
        """
        if value.position.player_idx != self.position.player_idx:
            # not self character, do nothing
            return value
        if value.cost.label & self.target_label == 0:
            # not weapon or artifact, do nothing
            return value
        # try decrease once
        if value.cost.decrease_cost(None):
            # decrease success
            if mode == "REAL":
                self.usage -= 1
        return value

    def event_handler_MOVE_OBJECT(
        self, event: MoveObjectEventArguments, match: Match
    ) -> List[RemoveObjectAction]:
        """
        As it triggers on equipping support,
        When move object end, check whether to remove.
        """
        return self.check_should_remove()


class SunyataFlower_4_4(EventCardBase):
    name: Literal["Sunyata Flower"]
    version: Literal["4.4"] = "4.4"
    cost: Cost = Cost()
    _accept_card_types: Type = PrivateAttr(SupportBase)
    _accept_class_list: List[str] | None = PrivateAttr(None)
    _accept_version: str | None = PrivateAttr(None)

    available_handler_in_deck: List[ActionTypes] = [ActionTypes.GAME_START]

    def _get_candidate_list(self, match: Match) -> List[str]:
        if self._accept_class_list is not None:
            return self._accept_class_list
        kwargs: Dict[str, Any] = {"exclude": set([self.name])}
        default_version = match.player_tables[
            self.position.player_idx
        ].player_deck_information.default_version
        if default_version is not None:
            kwargs["version"] = default_version
        self._accept_version = default_version
        candidate_list = get_class_list_by_base_class(self._accept_card_types, **kwargs)
        self._accept_class_list = candidate_list
        return candidate_list

    def event_handler_GAME_START(
        self, event: GameStartEventArguments, match: Match
    ) -> List[Actions]:
        """
        check all cards that able to generate. If they contains GAME_START
        event and available in deck, call them.
        """
        candidate_list = self._get_candidate_list(match)
        args = {}
        if self._accept_version is not None:
            args["version"] = self._accept_version
        candidate_instance = [
            get_instance(self._accept_card_types, {"name": name, **args})
            for name in candidate_list
        ]
        res: List[Actions] = []
        for i in candidate_instance:
            if ActionTypes.GAME_START in i.available_handler_in_deck:
                res += i.event_handler_GAME_START(event, match)
        return res

    def is_valid(self, match: Match) -> bool:
        return len(self.get_targets(match)) > 0

    def get_targets(self, match: Match) -> List[ObjectPosition]:
        """
        Our supports
        """
        supports = match.player_tables[self.position.player_idx].supports
        return [x.position for x in supports]

    def get_actions(
        self, target: ObjectPosition | None, match: Match
    ) -> List[RemoveObjectAction | CreateObjectAction]:
        """
        remove target, and generate 2 random support cards, and create status
        """
        assert target is not None
        ret: List[RemoveObjectAction | CreateObjectAction] = [
            RemoveObjectAction(object_position=target)
        ]
        candidate_list = self._get_candidate_list(match)
        for i in range(2):
            random_target = candidate_list[int(match._random() * len(candidate_list))]
            position = ObjectPosition(
                player_idx=self.position.player_idx, area=ObjectPositionType.HAND, id=-1
            )
            args = {}
            if self._accept_version is not None:
                args["version"] = self._accept_version
            ret.append(
                CreateObjectAction(
                    object_name=random_target,
                    object_position=position,
                    object_arguments=args,
                )
            )
        ret.append(
            CreateObjectAction(
                object_name=self.name,
                object_position=target.set_area(ObjectPositionType.TEAM_STATUS),
                object_arguments={},
            )
        )
        return ret


desc: Dict[str, DescDictType] = {
    "TEAM_STATUS/Sunyata Flower": {
        "names": {"en-US": "Sunyata Flower", "zh-CN": "净觉花"},
        "descs": {
            "4.4": {
                "en-US": "During the Round, the next time you play a Support Card: Spend 1 less Elemental Die.",  # noqa: E501
                "zh-CN": "本回合中，我方下次打出支援牌时：少花费1个元素骰。",  # noqa: E501
            }
        },
    },
    "CARD/Sunyata Flower": {
        "names": {"en-US": "Sunyata Flower", "zh-CN": "净觉花"},
        "descs": {
            "4.4": {
                "en-US": "Select a card from your Support Zone and discard it. After that, randomly generate 2 Support Cards in your hand.\nDuring the Round, the next time you play a Support Card: Spend 1 less Elemental Die.",  # noqa: E501
                "zh-CN": "选择一张我方支援区的牌，将其弃置。然后，在我方手牌中随机生成2张支援牌。\n本回合中，我方下次打出支援牌时：少花费1个元素骰。",  # noqa: E501
            }
        },
        "image_path": "cardface/Event_Event_Ganluhua.png",  # noqa: E501
        "id": 332029,
    },
}


register_class(SunyataFlower_4_4 | SunyataFlowerStatus_4_4, desc)
