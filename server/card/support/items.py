from typing import Any, List, Literal

from server.action import Actions
from server.event import UseCardEventArguments

from ...action import DrawCardAction, RemoveObjectAction

from ...event import SkillEndEventArguments

from ...struct import Cost
from ...consts import CostLabels, ObjectPositionType
from .base import RoundEffectSupportBase, SupportBase


class ItemBase(SupportBase):
    cost_label: int = CostLabels.CARD.value | CostLabels.ITEM.value


class RoundEffectItemBase(RoundEffectSupportBase):
    name: str
    desc: str
    version: str
    cost: Cost
    max_usage_per_round: int 
    cost_label: int = CostLabels.CARD.value | CostLabels.ITEM.value


class NRE(RoundEffectItemBase):
    name: Literal['NRE']
    desc: str = (
        'When played: Draw 1 Food Event Card from your deck. '
        'When you play a Food Event Card: Draw 1 Food Event Card from your '
        'deck. (Once per Round)'
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(any_dice_number = 2)
    max_usage_per_round: int = 1

    def draw_food_card(self) -> DrawCardAction:
        return DrawCardAction(
            player_idx = self.position.player_idx,
            number = 1,
            draw_if_filtered_not_enough = False,
            whitelist_cost_labels = CostLabels.FOOD.value
        )

    def play(self, match: Any) -> List[Actions]:
        return [self.draw_food_card()]

    def event_handler_USE_CARD(
        self, event: UseCardEventArguments, match: Any
    ) -> List[Actions]:
        if self.position.area == ObjectPositionType.SUPPORT:
            # on support area, do effect
            if self.usage <= 0:
                # usage is 0, do nothing
                return []
            if (
                event.action.card_position.player_idx 
                != self.position.player_idx
            ):
                # not our charactor use card, do nothing
                return []
            if event.card.cost.label & CostLabels.FOOD.value == 0:
                # not food card, do nothing
                return []
            # our use food card, draw new food card
            self.usage -= 1
            return [self.draw_food_card()]
        # otherwise, do normal response
        return super().event_handler_USE_CARD(event, match)


class TreasureSeekingSeelie(ItemBase):
    name: Literal['Treasure-Seeking Seelie']
    desc: str = (
        'Triggers automatically once per Round: This card gains 1 Pigeon. '
        'When this card gains 3 Pigeons, discard this card, then draw 1 card '
        'and create Genius Invokation TCG Omni Dice Omni Element x1.'
    )
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(same_dice_number = 1)
    usage: int = 0
    max_usage: int = 3

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[RemoveObjectAction | DrawCardAction]:
        """
        If our charactor use any skill, increase usage, and if usage
        reaches max_usage, draw 3 cards and remove self.
        """
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            source_area = ObjectPositionType.SUPPORT,
            target_area = ObjectPositionType.SKILL
        ):
            # not on support area, or not our charactor use skill
            return []
        # add usage
        self.usage += 1
        if self.usage != self.max_usage:
            # not reach max usage, do nothing
            return []
        # reach max usage, draw 3 cards and remove self
        return [
            DrawCardAction(
                player_idx = self.position.player_idx,
                number = 3,
                draw_if_filtered_not_enough = True
            ),
            RemoveObjectAction(
                object_position = self.position
            )
        ]


Items = NRE | TreasureSeekingSeelie
