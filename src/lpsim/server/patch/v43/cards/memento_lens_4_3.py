from typing import Any, Dict, List, Literal, Set, Type
from pydantic import PrivateAttr

from ....object_base import CreateSystemEventHandlerObject
from ....event_handler import SystemEventHandlerBase
from ....consts import ObjectPositionType
from ....modifiable_values import CostValue
from ....match import Match
from ....card.support.companions import CompanionBase
from ....card.support.locations import LocationBase
from ....card.equipment.artifact.base import ArtifactBase
from ....card.equipment.weapon.base import WeaponBase
from ....action import Actions
from ....event import UseCardEventArguments
from ....struct import Cost
from .....utils.class_registry import get_class_list_by_base_class, register_class
from .....utils.desc_registry import DescDictType
from ....card.support.items import RoundEffectItemBase


class MementoLensEventHandler_4_3(SystemEventHandlerBase):
    """
    Record used cards that matches type for both players.
    """

    name: Literal["Memento Lens"]
    version: Literal["4.3"] = "4.3"
    _accept_card_types: Type = PrivateAttr(
        WeaponBase | ArtifactBase | LocationBase | CompanionBase
    )
    _accept_class_name_set: Set[str] | None = PrivateAttr(None)
    card_used: List[Dict[str, int]] = [{}, {}]

    def _get_candidate_set(self, match: Match) -> Set[str]:
        if self._accept_class_name_set is not None:
            return self._accept_class_name_set
        kwargs: Dict[str, Any] = {}
        default_version = match.player_tables[
            self.position.player_idx
        ].player_deck_information.default_version
        if default_version is not None:
            kwargs["version"] = default_version
        candidate_list = get_class_list_by_base_class(self._accept_card_types, **kwargs)
        self._accept_class_name_set = set(candidate_list)
        return self._accept_class_name_set

    def event_handler_USE_CARD(
        self, event: UseCardEventArguments, match: Match
    ) -> List[Actions]:
        """
        If self played an accepted card type, record it.
        """
        player_idx = event.action.card_position.player_idx
        card_name = event.card_name
        if card_name not in self._get_candidate_set(match):
            # not accepted card type, do nothing
            return []
        self.card_used[player_idx][card_name] = 1
        return []


class MementoLens_4_3(CreateSystemEventHandlerObject, RoundEffectItemBase):
    name: Literal["Memento Lens"]
    version: Literal["4.3"] = "4.3"
    cost: Cost = Cost(same_dice_number=1)
    max_usage_per_round: int = 1
    handler_name: str = "Memento Lens"

    def value_modifier_COST(
        self, value: CostValue, match: Match, mode: Literal["REAL", "TEST"]
    ) -> CostValue:
        """
        If self played a card that name in played_card_names, and has usage,
        decrease 2 cost.
        """
        if self.usage <= 0:
            # no usage, do nothing
            return value
        if not self.position.check_position_valid(
            value.position,
            match,
            player_idx_same=True,
            source_area=ObjectPositionType.SUPPORT,
        ):
            # not self player or not in support, do nothing
            return value
        card = match.get_object(value.position)
        assert card is not None
        target_handler = self._get_event_handler(match)
        played_card_names = target_handler.card_used[self.position.player_idx]
        if card.name not in played_card_names:
            # not played card, do nothing
            return value
        # decrease cost
        result = [
            value.cost.decrease_cost(value.cost.elemental_dice_color),
            value.cost.decrease_cost(value.cost.elemental_dice_color),
        ]
        if any(result) and mode == "REAL":
            # decrease success and in real mode
            self.usage -= 1
        return value


desc: Dict[str, DescDictType] = {
    "SUPPORT/Memento Lens": {
        "names": {"en-US": "Memento Lens", "zh-CN": "留念镜"},
        "descs": {
            "4.3": {
                "en-US": "When you play a Weapon, Artifact, Location, or Companion card: If you have played a card with the same name previously during this match, spend 2 less Elemental Dice to play it. (Once per Round)\nUsage(s): 2",  # noqa: E501
                "zh-CN": "我方打出「武器」「圣遗物」「场地」「伙伴」手牌时：如果本场对局中我方曾经打出过所打出牌的同名卡牌，则少花费2个元素骰。（每回合1次）\n可用次数：2",  # noqa: E501
            }
        },
        "image_path": "cardface/Assist_Prop_Mirror.png",  # noqa: E501
        "id": 323006,
    },
    "SYSTEM/Memento Lens": {
        "names": {"en-US": "Memento Lens", "zh-CN": "留念镜"},
        "descs": {"4.3": {}},
    },
}


register_class(MementoLens_4_3 | MementoLensEventHandler_4_3, desc)
