from typing import Any, List, Literal

from ....modifiable_values import DamageValue

from ....consts import (
    DamageElementalType, DamageType, ObjectPositionType, SkillType
)

from ....action import MakeDamageAction

from ....event import SkillEndEventArguments

from ....struct import Cost
from .base import RoundEffectArtifactBase


class HealBySkillArtifactBase(RoundEffectArtifactBase):
    name: str
    desc: str
    version: str
    cost: Cost
    max_usage_per_round: int
    heal: int
    heal_skill_type: SkillType
    heal_target: Literal['SELF', 'TEAM']

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
            and event.action.skill_type == self.heal_skill_type
            and self.usage > 0
        ):
            # not equipped or not self use elemental skill or no usage
            return []
        self.usage -= 1
        action = MakeDamageAction(
            source_player_idx = self.position.player_idx,
            target_player_idx = self.position.player_idx,
            damage_value_list = [],
        )
        if self.heal_target == 'SELF':
            charactor = match.player_tables[
                self.position.player_idx].charactors[
                    self.position.charactor_idx]
            action.damage_value_list.append(
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.HEAL,
                    target_position = charactor.position,
                    damage = -self.heal,
                    damage_elemental_type = DamageElementalType.HEAL,
                    cost = self.cost.copy()
                )
            )
        else:
            charactors = match.player_tables[
                self.position.player_idx].charactors
            for charactor in charactors:
                if charactor.is_defeated:
                    continue
                action.damage_value_list.append(
                    DamageValue(
                        position = self.position,
                        damage_type = DamageType.HEAL,
                        target_position = charactor.position,
                        damage = -self.heal,
                        damage_elemental_type = DamageElementalType.HEAL,
                        cost = self.cost.copy()
                    )
                )
        return [action]


class AdventurersBandana(HealBySkillArtifactBase):
    name: Literal["Adventurer's Bandana"] = "Adventurer's Bandana"
    desc: str = (
        'After a character uses a Normal Attack: Heal self for 1 HP.'
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(same_dice_number = 1)
    max_usage_per_round: int = 3
    heal_skill_type: SkillType = SkillType.NORMAL_ATTACK
    heal: int = 1
    heal_target: Literal['SELF', 'TEAM'] = 'SELF'


class LuckyDogsSilverCirclet(HealBySkillArtifactBase):
    name: Literal["Lucky Dog's Silver Circlet"]
    desc: str = (
        'After a character uses an Elemental Skill: Heal self for 2 HP. '
        '(Once per Round)'
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(any_dice_number = 2)
    max_usage_per_round: int = 1
    heal_skill_type: SkillType = SkillType.ELEMENTAL_SKILL
    heal: int = 2
    heal_target: Literal['SELF', 'TEAM'] = 'SELF'


class TravelingDoctorsHandkerchief(HealBySkillArtifactBase):
    name: Literal["Traveling Doctor's Handkerchief"]
    desc: str = (
        'After a character uses an Elemental Burst: Heal all your characters '
        'for 1 HP. (Once per Round)'
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(same_dice_number = 1)
    max_usage_per_round: int = 1
    heal_skill_type: SkillType = SkillType.ELEMENTAL_BURST
    heal: int = 1
    heal_target: Literal['SELF', 'TEAM'] = 'TEAM'


HealBySkillArtifacts = (
    AdventurersBandana | LuckyDogsSilverCirclet | TravelingDoctorsHandkerchief
)
