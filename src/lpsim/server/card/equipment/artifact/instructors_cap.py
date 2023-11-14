from typing import Any, List, Literal

from .....utils.class_registry import register_class

from ....consts import (
    ELEMENT_TO_DIE_COLOR, ElementalReactionType, ObjectPositionType
)

from ....action import CreateDiceAction

from ....event import ReceiveDamageEventArguments, SkillEndEventArguments

from ....struct import Cost
from .base import RoundEffectArtifactBase


class InstructorsCap_3_3(RoundEffectArtifactBase):
    name: Literal["Instructor's Cap"]
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(any_dice_number = 2)
    max_usage_per_round: int = 3
    element_reaction_triggered: bool = False

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Any
    ) -> List[CreateDiceAction]:
        """
        Record if elemental reaction triggered
        """
        if event.elemental_reaction != ElementalReactionType.NONE:
            # has elemental reaction
            self.element_reaction_triggered = True
        return []

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[CreateDiceAction]:
        """
        if elemental reaction reiggered, and self use skill, and have usage,
        create one die with same element type as self.
        """
        if not self.element_reaction_triggered:
            # no elemental reaction triggered
            return []
        self.element_reaction_triggered = False
        if self.usage <= 0:
            # no usage
            return []
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            charactor_idx_same = True, 
            source_area = ObjectPositionType.CHARACTOR,
            target_area = ObjectPositionType.SKILL
        ):
            # not self player use skill or not equipped
            return []
        # create die
        self.usage -= 1
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        return [
            CreateDiceAction(
                player_idx = self.position.player_idx,
                number = 1,
                color = ELEMENT_TO_DIE_COLOR[charactor.element],
            )
        ]


register_class(InstructorsCap_3_3)
