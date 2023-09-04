from typing import Any, List, Literal

from server.action import Actions, CreateObjectAction
from server.event import RoundPrepareEventArguments, SkillEndEventArguments

from ...consts import (
    DamageElementalType, DieColor, ObjectPositionType, SkillType
)
from ...modifiable_values import (
    CostValue, DamageElementEnhanceValue, DamageIncreaseValue
)

from server.status.base import StatusBase
from .base import RoundCharactorStatus, UsageCharactorStatus


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
        if value.cost.decrease_cost(DieColor.GEO):  # pragma: no branch
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
        if (  # pragma: no branch
            value.damage_elemental_type == DamageElementalType.PHYSICAL
        ):
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


class RagingOniKing(RoundCharactorStatus):
    name: Literal['Raging Oni King'] = 'Raging Oni King'
    desc: str = (
        'The character to which this is attached to has their Normal Attacks '
        'deal +2 DMG, and their Physical DMG is converted to Geo DMG. '
        'After the character to which this is attached uses a Normal Attack: '
        'Gains Superlative Superstrength (Once per Round). '
        'Duration (Rounds): 2 '
    )
    version: Literal['3.6'] = '3.6'
    usage: int = 2
    max_usage: int = 2

    status_increase_usage: int = 1

    def renew(self, new_status: StatusBase) -> None:
        super().renew(new_status)
        # when renew, also renew status increase usage
        self.status_increase_usage = 1

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        # reset status increase usage
        self.status_increase_usage = 1
        return super().event_handler_ROUND_PREPARE(event, match)

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
        if (  # pragma: no branch
            value.damage_elemental_type == DamageElementalType.PHYSICAL
        ):
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

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        If self use normal attack, and has status increase usage, 
        gain superlative superstrength.
        """
        action = event.action
        if action.skill_type != SkillType.NORMAL_ATTACK:
            # not using normal attack
            return []
        if not self.position.check_position_valid(
            action.position, match, player_idx_same = True,
            charactor_idx_same = True,
        ):
            # not attack by self
            return []
        if self.status_increase_usage <= 0:
            # out of usage, not trigger
            return []
        # trigger
        self.status_increase_usage -= 1
        position = self.position.set_area(ObjectPositionType.CHARACTOR_STATUS)
        return [CreateObjectAction(
            object_position = position,
            object_name = 'Superlative Superstrength',
            object_arguments = {},
        )]


class SuperlativeSuperstrength(UsageCharactorStatus):
    name: Literal['Superlative Superstrength'] = 'Superlative Superstrength'
    desc: str = (
        'When the character to which this is attached to uses a Charged '
        'Attack: Deal +1 DMG. If the Usage(s) are no less than 2, '
        'expend 1 less Unaligned Element. '
        'Usage(s): 1 (Can stack. Max 3 stacks)'
    )
    version: Literal['3.6'] = '3.6'
    usage: int = 1
    max_usage: int = 3

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
        if not match.player_tables[self.position.player_idx].charge_satisfied:
            # not charged attack, not modify
            return value
        # modify damage
        assert self.usage > 0
        self.usage -= 1
        value.damage += 1
        return value

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['TEST', 'REAL']
    ) -> CostValue:
        """
        If self use charged attack, and has 2 or more usage, decrease one 
        unaligned die cost.
        """
        if self.usage < 2:
            # not enough usage, not modify
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
        if not match.player_tables[self.position.player_idx].charge_satisfied:
            # not charged attack, not modify
            return value
        # try decrease any cost
        value.cost.decrease_cost(None)
        return value


GeoCharactorStatus = SweepingTime | RagingOniKing | SuperlativeSuperstrength
