from typing import Any, Literal, List

from ....utils.class_registry import register_class

from ...action import RemoveObjectAction

from ...event import MakeDamageEventArguments

from ...consts import ElementType, IconType, SkillType

from ...modifiable_values import DamageIncreaseValue
from .base import RoundCharactorStatus


class HeavyStrike_3_7(RoundCharactorStatus):
    name: Literal['Heavy Strike'] = 'Heavy Strike'
    version: Literal['3.7'] = '3.7'
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.ATK_UP] = IconType.ATK_UP

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        """
        Increase damage for normal attack by 1 and decrease usage. 
        If it is charged attack, increase damage more 1.
        """
        assert mode == 'REAL'
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, SkillType.NORMAL_ATTACK
        ):
            # not this charactor use normal attack, not modify
            return value
        if self.usage <= 0:
            # no usage, not modify
            return value
        # this charactor use normal attack, increase damage by 1
        value.damage += 1
        # if it is charged attack, increase damage more 1
        if match.player_tables[self.position.player_idx].charge_satisfied:
            value.damage += 1
        # decrease usage
        self.usage -= 1
        return value

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        return self.check_should_remove()


class ShatteringIce_3_3(RoundCharactorStatus):
    name: Literal[
        'Elemental Resonance: Shattering Ice'
    ] = 'Elemental Resonance: Shattering Ice'
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.ATK_UP] = IconType.ATK_UP

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        """
        add 2 damage for skills.
        """
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, None
        ):
            # not this charactor use skill, do nothing
            return value
        if self.usage <= 0:
            # no usage, do nothing
            return value
        # we trigger elemental reaction, add 2 damage
        assert mode == 'REAL'
        self.usage -= 1
        value.damage += 2
        return value

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        """
        When make damage end, check whether to remove.
        """
        return self.check_should_remove()


class FerventFlames_3_3(RoundCharactorStatus):
    name: Literal[
        'Elemental Resonance: Fervent Flames'
    ] = 'Elemental Resonance: Fervent Flames'
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.ATK_UP] = IconType.ATK_UP

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        """
        If we trigger pyro elemental reaction, add 3 damage.
        """
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, None, False
        ):
            # not this charactor use skill, do nothing
            return value
        if ElementType.PYRO not in value.reacted_elements:
            # not trigger pyro elemental reaction, do nothing
            return value
        if self.usage <= 0:
            # no usage, do nothing
            return value
        # we trigger elemental reaction, add 2 damage
        assert mode == 'REAL'
        self.usage -= 1
        value.damage += 3
        return value

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        """
        When make damage end, check whether to remove.
        """
        return self.check_should_remove()


register_class(HeavyStrike_3_7 | ShatteringIce_3_3 | FerventFlames_3_3)
