from typing import Any, List, Literal

from ...struct import Cost

from ...action import MakeDamageAction, RemoveObjectAction

from ...event import MakeDamageEventArguments, SkillEndEventArguments

from ...consts import (
    DamageElementalType, DamageType, DieColor, ObjectPositionType, SkillType
)

from ...modifiable_values import (
    CostValue, DamageElementEnhanceValue, DamageIncreaseValue, DamageValue
)
from .base import (
    DefendCharactorStatus, ElementalInfusionCharactorStatus, 
    UsageCharactorStatus
)


class Stealth(DefendCharactorStatus, ElementalInfusionCharactorStatus):
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
    infused_elemental_type: DamageElementalType = DamageElementalType.PYRO

    def value_modifier_DAMAGE_ELEMENT_ENHANCE(
        self, value: DamageElementEnhanceValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageElementEnhanceValue:
        """
        When self use skill, and has talent, change physical to pyro
        """
        assert mode == 'REAL'
        charactor = match.player_tables[
            self.position.player_idx].charactors[self.position.charactor_idx]
        if charactor.talent is None:
            # no talent, do nothing
            return value
        return super().value_modifier_DAMAGE_ELEMENT_ENHANCE(
            value, match, mode
        )

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


class NiwabiEnshou(ElementalInfusionCharactorStatus, UsageCharactorStatus):
    name: Literal['Niwabi Enshou'] = 'Niwabi Enshou'
    desc: str = (
        'The character to which this is attached has their Normal Attacks '
        'deal +1 DMG, and their Physical DMG dealt converted to Pyro DMG.'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 2
    max_usage: int = 2
    infused_elemental_type: DamageElementalType = DamageElementalType.PYRO

    effect_triggered: bool = False

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        """
        If corresponding charactor use normal attack, increase damage by 1,
        and mark effect triggered.
        """
        assert mode == 'REAL'
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, SkillType.NORMAL_ATTACK
        ):
            # not this charactor use normal attack, not modify
            return value
        # this charactor use normal attack, modify
        self.usage -= 1
        self.effect_triggered = True
        value.damage += 1
        return value

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        """
        do not remove immediately here, as may trigger additional attack at
        skill end.
        """
        return []

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[MakeDamageAction | RemoveObjectAction]:
        """
        If effect triggered, and have talent on yoimiya, make 1 pyro damage.
        If usage is zero, then remove self.
        """
        ret: List[MakeDamageAction | RemoveObjectAction] = []
        if self.position.player_idx != event.action.position.player_idx:
            # not self player use skill
            self.effect_triggered = False
            return list(self.check_should_remove())
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        if (
            charactor.name == 'Yoimiya'
            and event.action.skill_type == SkillType.NORMAL_ATTACK
            and self.effect_triggered
            and charactor.talent is not None
        ):
            # yoimiya use normal attack and self effect triggered
            # and has talent, attack 1 pyro damage
            target = match.player_tables[
                1 - self.position.player_idx].get_active_charactor()
            ret.append(MakeDamageAction(
                source_player_idx = self.position.player_idx,
                target_player_idx = 1 - self.position.player_idx,
                damage_value_list = [
                    DamageValue(
                        position = self.position,
                        damage_type = DamageType.DAMAGE,
                        target_position = target.position,
                        damage = 1,
                        damage_elemental_type = DamageElementalType.PYRO,
                        cost = Cost(),
                    )
                ]
            ))
        # reset mark
        self.effect_triggered = False
        return ret + self.check_should_remove()


PyroCharactorStatus = Stealth | ExplosiveSpark | NiwabiEnshou
