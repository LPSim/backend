from typing import Any, List, Literal

from ....modifiable_values import DamageValue

from ....consts import (
    DamageElementalType, DamageType, ObjectPositionType, SkillType
)

from ....action import MakeDamageAction

from ....event import SkillEndEventArguments

from ....struct import Cost
from .base import RoundEffectArtifactBase


class LuckyDogsSilverCirclet(RoundEffectArtifactBase):
    name: Literal["Lucky Dog's Silver Circlet"]
    desc: str = (
        'After a character uses an Elemental Skill: Heal self for 2 HP. '
        '(Once per Round)'
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(any_dice_number = 2)
    max_usage_per_round: int = 1

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        If self use elemental skill, create one corresponding dice
        """
        if not (
            self.position.area == ObjectPositionType.CHARACTOR
            and event.action.position.player_idx == self.position.player_idx 
            and event.action.position.charactor_idx 
            == self.position.charactor_idx
            and event.action.skill_type == SkillType.ELEMENTAL_SKILL
            and self.usage > 0
        ):
            # not equipped or not self use elemental skill or no usage
            return []
        self.usage -= 1
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        return [MakeDamageAction(
            source_player_idx = self.position.player_idx,
            target_player_idx = self.position.player_idx,
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.HEAL,
                    target_position = charactor.position,
                    damage = -2,
                    damage_elemental_type = DamageElementalType.HEAL,
                    cost = self.cost.copy()
                )
            ],
        )]
