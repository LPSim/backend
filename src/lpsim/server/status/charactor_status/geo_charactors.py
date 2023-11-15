from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ..base import StatusBase

from ...action import Actions, CreateObjectAction

from ...event import RoundPrepareEventArguments, SkillEndEventArguments

from ...consts import (
    DamageElementalType, DieColor, IconType, ObjectPositionType, SkillType
)
from ...modifiable_values import (
    CostValue, DamageDecreaseValue, DamageElementEnhanceValue, 
    DamageIncreaseValue
)

from .base import (
    DefendCharactorStatus, ElementalInfusionCharactorStatus, 
    RoundCharactorStatus, UsageCharactorStatus
)


class SweepingTime_3_3(RoundCharactorStatus, ElementalInfusionCharactorStatus):
    name: Literal['Sweeping Time'] = 'Sweeping Time'
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    cost_decrease_usage: int = 1
    infused_elemental_type: DamageElementalType = DamageElementalType.GEO
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

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
        return super().value_modifier_DAMAGE_ELEMENT_ENHANCE(
            value, match, mode
        )

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


class RagingOniKing_4_2(RoundCharactorStatus, 
                        ElementalInfusionCharactorStatus):
    name: Literal['Raging Oni King'] = 'Raging Oni King'
    version: Literal['4.2'] = '4.2'
    usage: int = 2
    max_usage: int = 2
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS
    damage_increase: int = 1

    infused_elemental_type: DamageElementalType = DamageElementalType.GEO

    status_increase_usage: int = 1

    def __init__(self, *argv, **kwargs) -> None:
        super().__init__(*argv, **kwargs)

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
        return super().value_modifier_DAMAGE_ELEMENT_ENHANCE(
            value, match, mode)

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
        value.damage += self.damage_increase
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


class SuperlativeSuperstrength_3_6(UsageCharactorStatus):
    name: Literal['Superlative Superstrength'] = 'Superlative Superstrength'
    version: Literal['3.6'] = '3.6'
    usage: int = 1
    max_usage: int = 3
    icon_type: Literal[IconType.ATK_UP_ROCK] = IconType.ATK_UP_ROCK

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


class Stonehide_3_3(ElementalInfusionCharactorStatus, DefendCharactorStatus):
    """
    Combined Stonehide and Stone Force into one.
    """
    name: Literal['Stonehide'] = 'Stonehide'
    version: Literal['3.3'] = '3.3'
    usage: int = 3
    max_usage: int = 3

    min_damage_to_trigger: int = 1
    max_in_one_time: int = 1
    decrease_usage_by_damage: bool = False

    infused_elemental_type: DamageElementalType = DamageElementalType.GEO
    icon_type: Literal[IconType.BARRIER] = IconType.BARRIER

    damage_increase_usage: int = 1
    damage_increase_usage_max: int = 1

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        """
        Renew usage
        """
        self.damage_increase_usage = self.damage_increase_usage_max
        return []

    def value_modifier_DAMAGE_DECREASE(
        self, value: DamageDecreaseValue, match: Any, 
        mode: Literal['TEST', 'REAL']
    ) -> DamageDecreaseValue:
        value = super().value_modifier_DAMAGE_DECREASE(value, match, mode)
        # check if need to decrease usage 1 more
        if not value.is_corresponding_charactor_receive_damage(
            self.position, match
        ):
            # not corresponding charactor, return
            return value
        if value.damage_elemental_type != DamageElementalType.GEO:
            # not geo damage, return
            return value
        if self.usage > 0:
            # decrease usage
            self.usage -= 1
        return value

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        """
        Increase damage by 1
        """
        assert mode == 'REAL'
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, None
        ):
            # not corresponding charactor, return
            return value
        if self.damage_increase_usage <= 0:
            # no usage, return
            return value
        # increase damage
        value.damage += 1
        self.damage_increase_usage -= 1
        return value


class Petrification_3_7(RoundCharactorStatus):
    name: Literal['Petrification'] = 'Petrification'
    version: Literal['3.7'] = '3.7'
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS


class RagingOniKing_3_6(RagingOniKing_4_2):
    version: Literal['3.6']
    damage_increase: int = 2


register_class(
    SweepingTime_3_3 | RagingOniKing_4_2 | SuperlativeSuperstrength_3_6 
    | Stonehide_3_3 | Petrification_3_7 | RagingOniKing_3_6
)
