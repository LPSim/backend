from typing import Any, Dict, List, Literal, Type, get_args

from pydantic import PrivateAttr

from ....action import ActionTypes, Actions, CreateObjectAction
from .....utils.desc_registry import DescDictType
from .....utils.class_registry import (
    get_class_list_by_base_class, get_instance, register_class
)
from ....card.support.locations import LocationBase
from ....match import Match
from ....consts import IconType, ObjectPositionType
from ....event import GameStartEventArguments, UseCardEventArguments
from ....card.support.items import ItemBase
from ....card.event.foods import FoodCardBase
from ....struct import Cost, ObjectPosition
from ....card.support.base import UsageWithRoundRestrictionSupportBase
from ....card.support.companions import CompanionBase


class Mamere_4_3(CompanionBase, UsageWithRoundRestrictionSupportBase):
    name: Literal['Mamere']
    version: Literal['4.3'] = '4.3'
    cost: Cost = Cost()
    max_usage_one_round: int = 1
    usage: int = 3

    icon_type: Literal[IconType.TIMESTATE] = IconType.TIMESTATE

    _accept_card_types: Type = PrivateAttr(
        LocationBase | FoodCardBase | ItemBase | CompanionBase
    )

    available_handler_in_deck: List[ActionTypes] = [ActionTypes.GAME_START]

    def _get_candidate_list(self, match: Match) -> List[str]:
        kwargs: Dict[str, Any] = { 'exclude': set([self.name]) }
        default_version = match.player_tables[
            self.position.player_idx
        ].player_deck_information.default_version
        if default_version is not None:
            kwargs['version'] = default_version
        candidate_list = get_class_list_by_base_class(
            self._accept_card_types, 
            **kwargs
        )
        return candidate_list

    def event_handler_GAME_START(
        self, event: GameStartEventArguments, match: Match
    ) -> List[Actions]:
        """
        check all cards that able to generate. If they contains GAME_START
        event and available in deck, call them.
        """
        candidate_list = self._get_candidate_list(match)
        candidate_instance = [
            get_instance(self._accept_card_types, {
                'name': name, 'version': self.version
            }) for name in candidate_list
        ]
        res: List[Actions] = []
        for i in candidate_instance:
            if ActionTypes.GAME_START in i.available_handler_in_deck:
                res += i.event_handler_GAME_START(event, match)
        return res

    def event_handler_USE_CARD(
        self, event: UseCardEventArguments, match: Match
    ) -> List[Actions]:
        if self.position.area != ObjectPositionType.SUPPORT:
            # not placed to support, do original action
            return super().event_handler_USE_CARD(event, match)
        if not self.has_usage():
            # no usage, return
            return []
        if event.action.card_position.player_idx != self.position.player_idx:
            # not self use card, return
            return []
        card = event.card
        if card.name == 'Mamere':
            # using Mamere, return
            return []
        is_target_type = False
        for base_type in get_args(self._accept_card_types):
            if isinstance(card, base_type):
                is_target_type = True
                break
        if is_target_type:
            # using target type, generate new card
            candidate_list = self._get_candidate_list(match)
            # get candidate list for target type, except self
            random_target = candidate_list[
                int(match._random() * len(candidate_list))
            ]
            # use, and generate new card
            self.use()
            res: List[Actions] = []
            position = ObjectPosition(
                player_idx = self.position.player_idx,
                area = ObjectPositionType.HAND,
                id = -1
            )
            res.append(CreateObjectAction(
                object_name = random_target,
                object_position = position,
                object_arguments = {
                    'version': self.version
                }
            ))
            res += self.check_should_remove()
            return res
        return []


desc: Dict[str, DescDictType] = {
    "SUPPORT/Mamere": {
        "names": {
            "en-US": "Mamere",
            "zh-CN": "玛梅赫"
        },
        "descs": {
            "4.3": {
                "en-US": "After you play a Food/Location/Companion/Item Action Card other than Mamere: Randomly create 1 Food/Location/Companion/Item Action Card other than Mamere, and add it to your hand. (Once per Round).\nUsage(s): 3",  # noqa: E501
                "zh-CN": "我方打出「玛梅赫」以外的「料理」/「场地」/「伙伴」/「道具」行动牌后：随机生成1张「玛梅赫」以外的「料理」/「场地」/「伙伴」/「道具」行动牌，将其加入手牌。（每回合1次）\n可用次数：3"  # noqa: E501
            }
        },
        "image_path": "cardface/Assist_NPC_Mamere.png",  # noqa: E501
        "id": 322021
    },
}


register_class(Mamere_4_3, desc)
