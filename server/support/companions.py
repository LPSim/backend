from typing import Literal
from .support_base import SupportBase
from ..consts import (
    DiceCostLabels, ElementType, ELEMENT_TO_DIE_COLOR, ObjectPositionType,
    SkillType
)
from ..modifiable_values import DiceCostValue
from ..action import ActionBase, CreateDiceAction
from ..event import RoundEndEventArguments, SkillEndEventArguments


class CompanionBase(SupportBase):
    cost_label: int = (DiceCostLabels.CARD.value 
                       | DiceCostLabels.COMPANION.value)


class Rana(CompanionBase):
    name: Literal['Rana'] = 'Rana'
    version: Literal['3.7'] = '3.7'
    cost: DiceCostValue = DiceCostValue(same_dice_number = 2)
    usage: int = 1

    def event_handler_ROUND_PREPARE(self, event: RoundEndEventArguments) \
            -> list[ActionBase]:
        """
        When in round prepare, reset usage
        """
        self.usage = 1
        return []

    def act(self):
        """
        When activated, reset usage
        """
        self.usage = 1

    def event_handler_SKILL_END(self, event: SkillEndEventArguments) \
            -> list[CreateDiceAction]:
        """
        if it is in support are, and self player used a elemental skill,
        and have usage, and have next charactor, generate a die with color 
        of next charactor.
        """
        if (self.position.area == ObjectPositionType.SUPPORT
                and event.player_id == self.position.player_id 
                and event.skill_type == SkillType.ELEMENTAL_SKILL
                and self.usage > 0):
            table = event.match.player_tables[self.position.player_id]
            next_id = table.next_charactor_id()
            if next_id is not None:
                self.usage -= 1
                ele_type: ElementType = table.charactors[next_id].element
                die_color = ELEMENT_TO_DIE_COLOR[ele_type]
                return [CreateDiceAction(
                    player_id = self.position.player_id,
                    number = 1,
                    color = die_color,
                )]
        return []
