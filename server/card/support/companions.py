from typing import Any, Literal, List

from ...dice import Dice

from .base import SupportBase
from ...consts import (
    ELEMENT_DEFAULT_ORDER, CostLabels, DieColor, ElementType, 
    ELEMENT_TO_DIE_COLOR, ObjectPositionType, SkillType
)
from ...struct import Cost
from ...action import (
    Actions, ChangeObjectUsageAction, CreateDiceAction, DrawCardAction, 
    RemoveDiceAction, RemoveObjectAction
)
from ...event import (
    ChangeObjectUsageEventArguments, RoundEndEventArguments, 
    RoundPrepareEventArguments, SkillEndEventArguments
)


class CompanionBase(SupportBase):
    cost_label: int = (CostLabels.CARD.value 
                       | CostLabels.COMPANION.value)


class Timmie(CompanionBase):
    name: Literal['Timmie']
    desc: str = (
        'Triggers automatically once per Round: This card gains 1 Pigeon. '
        'When this card gains 3 Pigeons, discard this card, then draw 1 card '
        'and create Genius Invokation TCG Omni Dice Omni Element x1.'
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost()
    usage: int = 0
    max_usage: int = 3

    def play(self, match: Any) -> List[ChangeObjectUsageAction]:
        """
        When played, first reset usage to 0, then increase usage.
        """
        return [ChangeObjectUsageAction(
            object_position = self.position,
            change_type = 'DELTA',
            change_usage = 1
        )]

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        """
        When in round prepare, increase usage. 
        If usage is 3, remove self, draw a card and create a dice.
        """
        if self.position.area != ObjectPositionType.SUPPORT:
            # not in support area, do nothing
            return []
        return [ChangeObjectUsageAction(
            object_position = self.position,
            change_type = 'DELTA',
            change_usage = 1
        )]

    def event_handler_CHANGE_OBJECT_USAGE(
        self, event: ChangeObjectUsageEventArguments, match: Any
    ) -> List[RemoveObjectAction | DrawCardAction | CreateDiceAction]:
        """
        when self usage changed to 3, remove self, draw a card and create a 
        dice.
        """
        if self.position.area != ObjectPositionType.SUPPORT:
            # not in support area, do nothing
            return []
        if event.action.object_position.id != self.id:
            # not self
            return []
        ret: List[RemoveObjectAction | DrawCardAction | CreateDiceAction] = []
        if self.usage == 3:
            ret += [
                RemoveObjectAction(
                    object_position = self.position,
                ),
                DrawCardAction(
                    player_idx = self.position.player_idx,
                    number = 1,
                    draw_if_filtered_not_enough = True,
                ),
                CreateDiceAction(
                    player_idx = self.position.player_idx,
                    number = 1,
                    color = DieColor.OMNI,
                ),
            ]
        return ret


class Liben(CompanionBase):
    name: Literal['Liben']
    desc: str = (
        'End Phase: Collect your unused Elemental Dice (Max 1 of each '
        'Elemental Type). '
        'When Action Phase begins: If this card has collected 3 Elemental '
        'Dice, draw 2 cards and create Omni Element x2, then discard this '
        'card.'
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost()
    usage: int = 0
    max_usage: int = 3

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[RemoveDiceAction]:
        """
        Collect different color dice in round end.
        """
        if self.position.area != ObjectPositionType.SUPPORT:
            # not in support area, do nothing
            return []
        collect_order: List[DieColor] = []
        dice: Dice = match.player_tables[self.position.player_idx].dice
        colors = dice.colors
        # collect die in element default order
        for element in ELEMENT_DEFAULT_ORDER:
            color = ELEMENT_TO_DIE_COLOR[element]
            if color in colors:
                collect_order.append(color)
        # collect OMNI at last
        for color in colors:
            if color == DieColor.OMNI:
                collect_order.append(color)
        # only collect dice if usage is not full
        collect_order = collect_order[: self.max_usage - self.usage]
        self.usage += len(collect_order)
        return [RemoveDiceAction(
            player_idx = self.position.player_idx,
            dice_idxs = dice.colors_to_idx(collect_order)
        )]

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[CreateDiceAction | DrawCardAction | RemoveObjectAction]:
        """
        If this card has collected 3 Elemental Dice, draw 2 cards and create 
        Omni Element x2, then discard this card.'
        """
        if self.position.area != ObjectPositionType.SUPPORT:
            # not in support area, do nothing
            return []
        if self.usage != self.max_usage:
            # not enough dice collected
            return []
        return [ 
            CreateDiceAction(
                player_idx = self.position.player_idx,
                number = 2,
                color = DieColor.OMNI,
            ),
            DrawCardAction(
                player_idx = self.position.player_idx,
                number = 2,
                draw_if_filtered_not_enough = True
            ),
            RemoveObjectAction(
                object_position = self.position,
            ),
        ]


class Rana(CompanionBase):
    name: Literal['Rana']
    desc: str = (
        'After your character uses an Elemental Skill: '
        'Create 1 Elemental Die of the same Type as your next off-field '
        'character. (Once per Round)'
    )
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(same_dice_number = 2)
    usage: int = 1

    def play(self, match: Any) -> List[Actions]:
        """
        When played, reset usage.
        """
        self.usage = 1
        return super().play(match)

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        """
        When in round prepare, reset usage
        """
        self.usage = 1
        return []

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[CreateDiceAction]:
        """
        if it is in support are, and self player used a elemental skill,
        and have usage, and have next charactor, generate a die with color 
        of next charactor.
        """
        if (
            self.position.area == ObjectPositionType.SUPPORT
            and event.action.position.player_idx == self.position.player_idx 
            and event.action.skill_type == SkillType.ELEMENTAL_SKILL
            and self.usage > 0
        ):
            table = match.player_tables[self.position.player_idx]
            next_idx = table.next_charactor_id()
            if next_idx is not None:
                self.usage -= 1
                ele_type: ElementType = table.charactors[next_idx].element
                die_color = ELEMENT_TO_DIE_COLOR[ele_type]
                return [CreateDiceAction(
                    player_idx = self.position.player_idx,
                    number = 1,
                    color = die_color,
                )]
        return []


Companions = Timmie | Liben | Rana
