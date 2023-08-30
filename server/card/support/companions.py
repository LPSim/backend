from typing import Literal, List
from .support_base import SupportBase
from ...consts import (
    CostLabels, DieColor, ElementType, ELEMENT_TO_DIE_COLOR, 
    ObjectPositionType, SkillType
)
from ...struct import Cost
from ...action import (
    ActionBase, Actions, CreateDiceAction, DrawCardAction, RemoveObjectAction
)
from ...event import RoundPrepareEventArguments, SkillEndEventArguments


class CompanionBase(SupportBase):
    cost_label: int = (CostLabels.CARD.value 
                       | CostLabels.COMPANION.value)


class Timmie(CompanionBase):
    name: Literal['Timmie'] = 'Timmie'
    desc: str = (
        'Triggers automatically once per Round: This card gains 1 Pigeon. '
        'When this card gains 3 Pigeons, discard this card, then draw 1 card '
        'and create Genius Invokation TCG Omni Dice Omni Element x1.'
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost()
    usage: int = 1

    def event_handler_ROUND_PREPARE(self, event: RoundPrepareEventArguments) \
            -> List[Actions]:
        """
        When in round prepare, increase usage. If usage is 3, remove self,
        draw a card and create a dice.
        """
        if self.position.area != ObjectPositionType.SUPPORT:
            # not in support area, do nothing
            return []
        ret: List[Actions] = []
        self.usage += 1
        if self.usage == 3:
            ret += [
                RemoveObjectAction(
                    object_position = self.position,
                    object_id = self.id,
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


class Rana(CompanionBase):
    name: Literal['Rana'] = 'Rana'
    desc: str = (
        'After your character uses an Elemental Skill: '
        'Create 1 Elemental Die of the same Type as your next off-field '
        'character. (Once per Round)'
    )
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(same_dice_number = 2)
    usage: int = 1

    def event_handler_ROUND_PREPARE(self, event: RoundPrepareEventArguments) \
            -> list[ActionBase]:
        """
        When in round prepare, reset usage
        """
        self.usage = 1
        return []

    def event_handler_SKILL_END(self, event: SkillEndEventArguments) \
            -> list[CreateDiceAction]:
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
            table = event.match.player_tables[self.position.player_idx]
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


Companions = Timmie | Rana
