from typing import Any, List, Literal

from ...action import DrawCardAction, RemoveObjectAction

from ...event import SkillEndEventArguments

from ...struct import Cost
from ...consts import CostLabels, ObjectPositionType
from .base import SupportBase


class ItemBase(SupportBase):
    cost_label: int = CostLabels.CARD.value | CostLabels.ITEM.value


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


Items = TreasureSeekingSeelie | TreasureSeekingSeelie
