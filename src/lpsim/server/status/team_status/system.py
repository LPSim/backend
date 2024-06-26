"""
Team status generated by system.
"""

from typing import Any, Literal

from ....utils.class_registry import register_class
from .base import ShieldTeamStatus, UsageTeamStatus
from ...modifiable_values import DamageIncreaseValue
from ...consts import DamageElementalType, DamageType, IconType


class CatalyzingField_3_4(UsageTeamStatus):
    """
    Catalyzing field.
    """

    name: Literal["Catalyzing Field"] = "Catalyzing Field"
    version: Literal["3.4"] = "3.4"
    usage: int = 2
    max_usage: int = 2
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any, mode: Literal["TEST", "REAL"]
    ) -> DamageIncreaseValue:
        """
        Increase damage for dendro or electro damages, and decrease usage.
        """
        if value.damage_type != DamageType.DAMAGE:
            # not damage, not modify
            return value
        if not self.position.check_position_valid(
            value.position,
            match,
            player_idx_same=True,
        ):
            # source not self, not activate
            return value
        if not self.position.check_position_valid(
            value.target_position,
            match,
            player_idx_same=False,
            target_is_active_character=True,
        ):
            # target not enemy, or target not active character, not activate
            return value
        if (
            value.damage_elemental_type
            in [
                DamageElementalType.DENDRO,
                DamageElementalType.ELECTRO,
            ]
            and self.usage > 0
        ):
            value.damage += 1
            assert mode == "REAL"
            self.usage -= 1
        return value


class CatalyzingField_3_3(CatalyzingField_3_4):
    """
    Catalyzing field.
    """

    version: Literal["3.3"] = "3.3"
    usage: int = 3
    max_usage: int = 3


class DendroCore_3_3(UsageTeamStatus):
    """
    Dendro core.
    """

    name: Literal["Dendro Core"] = "Dendro Core"
    version: Literal["3.3"] = "3.3"
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any, mode: Literal["TEST", "REAL"]
    ) -> DamageIncreaseValue:
        """
        Increase damage for electro or pyro damages by 2, and decrease usage.
        """
        if value.damage_type != DamageType.DAMAGE:
            # not damage, not modify
            return value
        if not self.position.check_position_valid(
            value.position,
            match,
            player_idx_same=True,
        ):
            # source not self, not activate
            return value
        if not self.position.check_position_valid(
            value.target_position,
            match,
            player_idx_same=False,
            target_is_active_character=True,
        ):
            # target not enemy, or target not active character, not activate
            return value
        if (
            value.damage_elemental_type
            in [
                DamageElementalType.ELECTRO,
                DamageElementalType.PYRO,
            ]
            and self.usage > 0
        ):
            value.damage += 2
            assert mode == "REAL"
            self.usage -= 1
        return value


class Crystallize_3_3(ShieldTeamStatus):
    """
    Crystallize.
    """

    name: Literal["Crystallize"] = "Crystallize"
    version: Literal["3.3"] = "3.3"
    usage: int = 1
    max_usage: int = 2


register_class(
    CatalyzingField_3_4 | CatalyzingField_3_3 | DendroCore_3_3 | Crystallize_3_3
)
