from typing import Any, Literal, List

from ...action import RemoveObjectAction

from ...event import MakeDamageEventArguments

from ...consts import ElementType, IconType, SkillType

from ...modifiable_values import DamageIncreaseValue
from .base import RoundCharactorStatus


class HeavyStrike(RoundCharactorStatus):
    name: Literal['Heavy Strike'] = 'Heavy Strike'
    desc: str = (
        "During this round, your current active character's next "
        'Normal Attack deals +1 DMG. '
        'When this Normal Attack is a Charged Attack: Deal +1 additional DMG.'
    )
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


class ShatteringIce(RoundCharactorStatus):
    name: Literal[
        'Elemental Resonance: Shattering Ice'
    ] = 'Elemental Resonance: Shattering Ice'
    desc: str = (
        'During this Round, your character will deal +2 DMG '
        'for the next instance.'
    )
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


class FerventFlames(RoundCharactorStatus):
    name: Literal[
        'Elemental Resonance: Fervent Flames'
    ] = 'Elemental Resonance: Fervent Flames'
    desc: str = (
        'During this round, the next instance of Pyro-Related Reactions your '
        'character triggers deals +3 DMG.'
    )
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
            self.position, match, None
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


EventCardCharactorStatus = HeavyStrike | ShatteringIce | FerventFlames
