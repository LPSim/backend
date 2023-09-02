from typing import Any, List, Literal

from server.action import Actions
from server.event import RoundPrepareEventArguments

from ...consts import (
    DamageElementalType, DieColor, ObjectPositionType, SkillType
)
from ...modifiable_values import (
    CostValue, DamageElementEnhanceValue, DamageIncreaseValue
)

from server.status.base import StatusBase
from .base import RoundCharactorStatus


class SweepingTime(RoundCharactorStatus):
    name: Literal['Sweeping Time'] = 'Sweeping Time'
    desc: str = (
        'When your character uses a Normal Attack: Consume 1 less Geo Die. '
        '(Once per Round) '
        "Character's Normal Attacks deal +2 DMG, and their Physical DMG is "
        'converted to Geo DMG. '
        'Duration (Rounds): 2'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    cost_decrease_usage: int = 1

    def renew(self, new_status: StatusBase) -> None:
        super().renew(new_status)
        # when renew, also renew cost decrease usage
        self.cost_decrease_usage = 1

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        # reset cost decrease usage
        self.cost_decrease_usage = 1
        return super().event_handler_ROUND_PREPARE(event, match)

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['TEST', 'REAL']
    ) -> CostValue:
        """
        If self use normal attack, and not decreased this round, and has
        cost, then decrease one geo die cost.
        """
        if self.cost_decrease_usage <= 0:
            # out of usage, not modify
            return value
        if not self.position.check_position_valid(
            value.position, match, player_idx_same = True, 
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL,
        ):
            # not this charactor use skill, not modify
            return value
        skill = match.get_object(value.position)
        skill_type: SkillType = skill.skill_type
        if skill_type != SkillType.NORMAL_ATTACK:
            # not normal attack, not modify
            return value
        # decrease geo cost
        if value.cost.decrease_cost(DieColor.GEO):
            # decrease success
            if mode == 'REAL':
                self.cost_decrease_usage -= 1
        return value

    def value_modifier_DAMAGE_ELEMENT_ENHANCE(
        self, value: DamageElementEnhanceValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageElementEnhanceValue:
        assert mode == 'REAL'
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, SkillType.NORMAL_ATTACK
        ):
            # not this charactor use normal attack, not modify
            return value
        # modify element
        if value.damage_elemental_type == DamageElementalType.PHYSICAL:
            # physical, change to geo
            value.damage_elemental_type = DamageElementalType.GEO
        return value

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        assert mode == 'REAL'
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, SkillType.NORMAL_ATTACK
        ):
            # not this charactor use normal attack, not modify
            return value
        # modify damage
        value.damage += 2
        return value


GeoCharactorStatus = SweepingTime | SweepingTime
