from typing import Any, List, Literal
from server.dice import Dice

from server.action import Actions, CreateDiceAction, RemoveDiceAction
from ...event import RoundEndEventArguments, RoundPrepareEventArguments

from ...struct import Cost
from ...consts import (
    ELEMENT_DEFAULT_ORDER, ELEMENT_TO_DIE_COLOR, CostLabels, DieColor
)
from .base import SupportBase


class LocationBase(SupportBase):
    cost_label: int = CostLabels.CARD.value | CostLabels.LOCATION.value


class Vanarana(LocationBase):
    name: Literal['Vanarana']
    desc: str = (
        'End Phase: Collect up to 2 unused Elemental Dice. '
        'When the Action Phase begins: Reclaim the dice you collected using '
        'this card.'
    )
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost()
    usage: int = 0
    colors: List[DieColor] = []

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)

    def play(self, match: Any) -> List[Actions]:
        self.usage = 0
        self.colors = []
        return super().play(match)

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[CreateDiceAction]:
        """
        When in round prepare, give collected dice back.
        """
        assert self.usage == len(self.colors)
        if self.position.area != 'SUPPORT':
            # not in support area, do nothing
            return []
        if self.usage == 0:
            # no dice, do nothing
            return []
        ret: List[CreateDiceAction] = []
        for color in self.colors:
            ret.append(CreateDiceAction(
                player_idx = self.position.player_idx,
                color = color,
                number = 1
            ))
        self.usage = 0
        self.colors = []
        return ret

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[RemoveDiceAction]:
        """
        When in round end, collect up to 2 unused elemental dice.
        """
        if self.position.area != 'SUPPORT':
            # not in support area, do nothing
            return []
        assert self.usage == 0 and len(self.colors) == 0
        current_dice: Dice = match.player_tables[
            self.position.player_idx].dice
        current_dice_colors = current_dice.colors
        if len(current_dice_colors) == 0:
            # no dice, do nothing
            return []
        dice_map = {}
        for color in current_dice_colors:
            if color not in dice_map:
                dice_map[color] = 0
            dice_map[color] += 1
        # first try to gather two same element dice
        for element in ELEMENT_DEFAULT_ORDER:
            color = ELEMENT_TO_DIE_COLOR[element]
            if (
                color in dice_map 
                and dice_map[color] >= 2
                and len(self.colors) < 2
            ):
                self.colors = [color, color]
        if len(self.colors) < 2:
            # if not enough, gather any two dice
            for element in ELEMENT_DEFAULT_ORDER:
                color = ELEMENT_TO_DIE_COLOR[element]
                if color in dice_map and len(self.colors) < 2:
                    self.colors.append(color)
        if len(self.colors) < 2:
            # if not enough, gather omni
            if DieColor.OMNI in dice_map:
                self.colors.append(DieColor.OMNI)
                if len(self.colors) < 2 and dice_map[DieColor.OMNI] >= 2:
                    self.colors.append(DieColor.OMNI)
        self.usage = len(self.colors)
        dice_idxs = current_dice.colors_to_idx(self.colors)
        return [RemoveDiceAction(
            player_idx = self.position.player_idx,
            dice_idxs = dice_idxs,
        )]


Locations = Vanarana | Vanarana