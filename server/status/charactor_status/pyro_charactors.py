from typing import Any, Literal

from ...consts import (
    DamageElementalType, DieColor, ObjectPositionType, SkillType
)

from ...modifiable_values import (
    CostValue, DamageElementEnhanceValue, DamageIncreaseValue
)
from .base import DefendCharactorStatus, UsageCharactorStatus


class Stealth(DefendCharactorStatus):
    name: Literal['Stealth'] = 'Stealth'
    desc: str = (
        'The character to which this is attached takes -1 DMG and '
        'deals +1 DMG. Usage(s): 2'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    min_damage_to_trigger: int = 1
    max_in_one_time: int = 1

    def value_modifier_DAMAGE_ELEMENT_ENHANCE(
        self, value: DamageElementEnhanceValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageElementEnhanceValue:
        """
        When self use skill, and has talent, change physical to pyro
        """
        assert mode == 'REAL'
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, None
        ):
            # not corresponding charactor use skill, do nothing
            return value
        if self.usage <= 0:  # pragma: no cover
            # no usage, do nothing
            return value
        charactor = match.player_tables[
            self.position.player_idx].charactors[self.position.charactor_idx]
        if charactor.talent is None:
            # no talent, do nothing
            return value
        # change physical to pyro
        if value.damage_elemental_type == DamageElementalType.PHYSICAL:
            value.damage_elemental_type = DamageElementalType.PYRO
        return value

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        """
        When self use skill, increase damage by 1
        """
        assert mode == 'REAL'
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, None
        ):
            # not corresponding charactor use damage skill, do nothing
            return value
        if self.usage <= 0:  # pragma: no cover
            # no usage, do nothing
            return value
        # increase damage by 1
        value.damage += 1
        self.usage -= 1
        return value


class ExplosiveSpark(UsageCharactorStatus):
    name: Literal['Explosive Spark'] = 'Explosive Spark'
    desc: str = (
        'When the character to which this is attached to uses a Charged '
        'Attack: Spend 1 less Pyro Die and deal +1 DMG. Usage(s): XXX'
    )
    version: Literal['3.4'] = '3.4'
    usage: int
    max_usage: int

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.desc = self.desc.replace('XXX', str(self.max_usage))

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
        If self use charged attack, decrease one 
        unaligned die cost.
        """
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
        # try decrease pyro cost
        value.cost.decrease_cost(DieColor.PYRO)
        return value


PyroCharactorStatus = Stealth | ExplosiveSpark
