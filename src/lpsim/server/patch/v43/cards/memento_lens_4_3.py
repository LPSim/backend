from typing import Dict, List, Literal, Tuple, Type

from pydantic import PrivateAttr

from ....consts import ObjectPositionType
from ....modifiable_values import CostValue
from ....match import Match
from ....card.support.companions import CompanionBase
from ....card.support.locations import LocationBase
from ....card.equipment.artifact.base import ArtifactBase
from ....card.equipment.weapon.base import WeaponBase
from ....action import ActionTypes, Actions
from ....event import UseCardEventArguments
from ....struct import Cost
from .....utils.class_registry import register_class
from .....utils.desc_registry import DescDictType
from ....card.support.items import RoundEffectItemBase


class MementoLens_4_3(RoundEffectItemBase):
    name: Literal["Memento Lens"]
    version: Literal["4.3"] = "4.3"
    cost: Cost = Cost(same_dice_number = 1)
    played_card_names: Dict[str, int] = {}
    _accept_card_types: Tuple[Type] = PrivateAttr(
        (WeaponBase, ArtifactBase, LocationBase, CompanionBase)
    )
    max_usage_per_round: int = 1
    # mark USE_CARD as avaliable in deck to record used cards
    available_handler_in_deck: List[ActionTypes] = [
        ActionTypes.USE_CARD, 
    ]

    def event_handler_USE_CARD(
        self, event: UseCardEventArguments, match: Match
    ) -> List[Actions]:
        """
        If self played an accepted card type, record it.
        """
        if event.action.card_position.id == self.id:
            # self, do normal play
            return super().event_handler_USE_CARD(event, match)
        if event.action.card_position.player_idx != self.position.player_idx:
            # not self play, do nothing
            return []
        card = event.card
        if not isinstance(card, self._accept_card_types):
            # not accepted card type, do nothing
            return []
        self.played_card_names[card.name] = 1
        return []

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
            value.position, match, player_idx_same = True,
            source_area = ObjectPositionType.SUPPORT
        ):
            # not self player or not in support, do nothing
            return value
        card = match.get_object(value.position)
        assert card is not None
        if card.name not in self.played_card_names:
            # not played card, do nothing
            return value
        # decrease cost
        result = [
            value.cost.decrease_cost(value.cost.elemental_dice_color),
            value.cost.decrease_cost(value.cost.elemental_dice_color),
        ]
        if any(result) and mode == 'REAL':
            # decrease success and in real mode
            self.usage -= 1
        return value


desc: Dict[str, DescDictType] = {
    "SUPPORT/Memento Lens": {
        "names": {
            "en-US": "Memento Lens",
            "zh-CN": "留念镜"
        },
        "descs": {
            "4.3": {
                "en-US": "When you play a Weapon, Artifact, Location, or Companion card: If you have played a card with the same name previously during this match, spend 2 less Elemental Dice to play it. (Once per Round)\nUsage(s): 2",  # noqa: E501
                "zh-CN": "我方打出「武器」「圣遗物」「场地」「伙伴」手牌时：如果本场对局中我方曾经打出过所打出牌的同名卡牌，则少花费2个元素骰。（每回合1次）\n可用次数：2"  # noqa: E501
            }
        },
        "image_path": "cardface/Assist_Prop_Mirror.png",  # noqa: E501
        "id": 323006
    },
}


register_class(MementoLens_4_3, desc)
