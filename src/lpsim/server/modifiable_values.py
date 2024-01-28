from enum import Enum
from typing import List, Any
from ..utils import BaseModel
from .consts import (
    DieColor,
    DamageType,
    DamageElementalType,
    ElementalReactionType,
    ElementType,
    ObjectPositionType,
    SkillType,
)
from .struct import ObjectPosition, Cost


class ModifiableValueTypes(str, Enum):
    """
    Enum representing the type of a modifiable value. A modifiable value is a
    value that can be modified by other objects before being used.
    """

    INITIAL_DICE_COLOR = "INITIAL_DICE_COLOR"
    REROLL = "REROLL"
    COMBAT_ACTION = "COMBAT_ACTION"

    # Cost is used in most situations that decrease cost. Full cost is used
    # only for effects that should decrease cost to 0, which is performed after
    # normal cost decrease. Until 4.2, only Timaeus and Wagner has this effect.
    COST = "COST"
    FULL_COST = "FULL_COST"

    # damage calculation is split into 4 parts: increase, multiply and
    # decrease. damage will be first increased, then multiplied,
    # then decreased.
    DAMAGE_ELEMENT_ENHANCE = "DAMAGE_ELEMENT_ENHANCE"
    DAMAGE_INCREASE = "DAMAGE_INCREASE"
    DAMAGE_MULTIPLY = "DAMAGE_MULTIPLY"
    DAMAGE_DECREASE = "DAMAGE_DECREASE"

    # before using card, a modifiable value is used to check whether use card
    # successfully.
    USE_CARD = "USE_CARD"


class ModifiableValueBase(BaseModel):
    """
    Base class of modifiable values. It saves the value and can pass through
    value modifiers to update its value in-place.
    """

    type: ModifiableValueTypes
    position: ObjectPosition


class InitialDiceColorValue(ModifiableValueBase):
    type: ModifiableValueTypes = ModifiableValueTypes.INITIAL_DICE_COLOR
    player_idx: int
    dice_colors: List[DieColor] = []


class RerollValue(ModifiableValueBase):
    type: ModifiableValueTypes = ModifiableValueTypes.REROLL
    value: int
    player_idx: int


class CostValue(ModifiableValueBase):
    type: ModifiableValueTypes = ModifiableValueTypes.COST
    target_position: ObjectPosition | None
    cost: Cost

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        self.cost = self.cost.copy()
        if self.cost.original_value is None:  # pragma: no branch
            self.cost.original_value = self.cost.copy()


class FullCostValue(CostValue):
    type: ModifiableValueTypes = ModifiableValueTypes.FULL_COST

    def __init__(self, *argv, **kwargs):
        # full cost is used after normal cost decrease, so no need to refresh
        # its original value, just copy normal cost value.
        BaseModel.__init__(self, *argv, **kwargs)

    @staticmethod
    def from_cost_value(value: CostValue) -> "FullCostValue":
        return FullCostValue(
            position=value.position,
            target_position=value.target_position,
            cost=value.cost,
        )


class CombatActionValue(ModifiableValueBase):
    type: ModifiableValueTypes = ModifiableValueTypes.COMBAT_ACTION
    action_label: int
    do_combat_action: bool


class DamageElementEnhanceValue(ModifiableValueBase):
    """
    It describes a detailed damage, i.e. character X will receive the damage.
    It contains all information that a damage is needed, except element
    reaction, as it is not decided yet.

    It is the initial stage of damage calculation.
    In this stage, buffs will modify the damage elemental type.
    """

    type: ModifiableValueTypes = ModifiableValueTypes.DAMAGE_ELEMENT_ENHANCE
    damage_type: DamageType
    target_position: ObjectPosition
    damage: int
    damage_elemental_type: DamageElementalType
    cost: Cost  # original cost of source

    damage_from_element_reaction: bool = False

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        if self.damage_type == DamageType.HEAL:
            assert self.damage < 0, "Heal should be negative"
            assert (
                self.damage_elemental_type == DamageElementalType.HEAL
            ), "Heal should be heal type"
        elif self.damage_type == DamageType.DAMAGE:
            assert self.damage >= 0, "Damage should be non-negative"
        else:
            assert self.damage_type == DamageType.ELEMENT_APPLICATION
            assert self.damage == 0, "Element application should be 0"

    def copy(self, *argv, **kwargs) -> "DamageElementEnhanceValue":
        assert (
            len(argv) == 0 and len(kwargs) == 0
        ), "No parameters are allowed when copying."
        return DamageElementEnhanceValue(
            position=self.position,
            damage_type=self.damage_type,
            target_position=self.target_position,
            damage=self.damage,
            damage_elemental_type=self.damage_elemental_type,
            cost=self.cost.copy(),
            damage_from_element_reaction=self.damage_from_element_reaction,
        )

    def is_corresponding_character_use_damage_skill(
        self,
        object_position: ObjectPosition,
        match: Any,
        skill_type: SkillType | None,
        ignore_elemental_reaction: bool = True,
    ) -> bool:
        """
        Most objects modifying damage when current character
        makes damages by using skills. This function checks if the object
        with given object_position is the corresponding character using skill.

        If object position is on certain character, i.e. equipment or
        character status, the character should match damage source. Otherwise,
        the active character should be the damage source.

        Args:
            object_position: The position of the object to check.
            match: The match object.
            skill_type: If not None, the skill type should match.
            ignore_elemental_reaction: If True, elemental reaction damages will
                not be considered.
        """
        if self.damage_type != DamageType.DAMAGE:
            # not damage
            return False
        if self.position.area != ObjectPositionType.SKILL:
            # not skill
            return False
        if self.position.player_idx != object_position.player_idx:
            # not same player
            return False
        if (
            object_position.area == ObjectPositionType.CHARACTER
            or object_position.area == ObjectPositionType.CHARACTER_STATUS
        ):
            # object on character, get idx
            character_idx = object_position.character_idx
        else:
            # not on character, get active character idx
            character_idx = match.player_tables[
                object_position.player_idx
            ].active_character_idx
        if self.position.character_idx != character_idx:
            # not same character
            return False
        if ignore_elemental_reaction and self.damage_from_element_reaction:
            # elemental reaction damage
            return False
        if skill_type is not None:
            skill = match.get_object(self.position)
            if skill.skill_type != skill_type:
                # skill type not match
                return False
        return True

    def is_corresponding_character_receive_damage(
        self, object_position: ObjectPosition, match: Any, ignore_piercing: bool = True
    ) -> bool:
        """
        Most objects modifying damage only when current character
        receives damages. This function checks if the object with given
        object_position is the corresponding character receiving damage.

        If object position is on certain character, i.e. equipment or
        character status, the character should match damage target. Otherwise,
        the active character should be the damage target.

        Args:
            object_position: The position of the object to check.
            match: The match object.
            ignore_piercing: If True, piercing damage will result in False.
        """
        if self.damage_type != DamageType.DAMAGE:
            # not damage
            return False
        if (
            ignore_piercing
            and self.damage_elemental_type == DamageElementalType.PIERCING
        ):
            # piercing damage
            return False
        if (
            self.target_position.area != ObjectPositionType.CHARACTER
        ):  # pragma: no cover
            # not on character
            return False
        if self.target_position.player_idx != object_position.player_idx:
            # not same player
            return False
        if (
            object_position.area == ObjectPositionType.CHARACTER
            or object_position.area == ObjectPositionType.CHARACTER_STATUS
        ):
            # object on character, get idx
            character_idx = object_position.character_idx
        else:
            # not on character, get active character idx
            character_idx = match.player_tables[
                object_position.player_idx
            ].active_character_idx
        if self.target_position.character_idx != character_idx:
            # not same character
            return False
        return True


class DamageIncreaseValue(DamageElementEnhanceValue):
    """
    It inherits DamageElementEnhanceValue, and add two information about
    elemental reaction.

    In this stage, damage elemental type has been decided, and all add-type
    damage buffs will modify the damage, including elemental reaction.
    """

    type: ModifiableValueTypes = ModifiableValueTypes.DAMAGE_INCREASE

    element_reaction: ElementalReactionType
    reacted_elements: List[ElementType]

    @staticmethod
    def from_element_enhance_value(
        value: DamageElementEnhanceValue,
        element_reaction: ElementalReactionType,
        reacted_elements: List[ElementType],
    ) -> "DamageIncreaseValue":
        return DamageIncreaseValue(
            position=value.position,
            damage_type=value.damage_type,
            target_position=value.target_position,
            damage=value.damage,
            damage_elemental_type=value.damage_elemental_type,
            cost=value.cost,
            damage_from_element_reaction=value.damage_from_element_reaction,
            element_reaction=element_reaction,
            reacted_elements=reacted_elements,
        )


class DamageMultiplyValue(DamageIncreaseValue):
    """
    In this stage, damage increase has been decided, and all multiply-type
    buffs will modify the damage, e.g. Mona elemental burst, Noelle elemental
    skill.
    """

    type: ModifiableValueTypes = ModifiableValueTypes.DAMAGE_MULTIPLY

    @staticmethod
    def from_increase_value(
        increase_value: DamageIncreaseValue,
    ) -> "DamageMultiplyValue":
        return DamageMultiplyValue(
            position=increase_value.position,
            damage_type=increase_value.damage_type,
            target_position=increase_value.target_position,
            damage=increase_value.damage,
            damage_elemental_type=increase_value.damage_elemental_type,
            damage_from_element_reaction=increase_value.damage_from_element_reaction,
            cost=increase_value.cost,
            element_reaction=increase_value.element_reaction,
            reacted_elements=increase_value.reacted_elements,
        )


class DamageDecreaseValue(DamageIncreaseValue):
    """
    In this stage, damage multiply has been decided, and all decrease-type
    buffs will modify the damage, i.e. various types of shields.
    """

    type: ModifiableValueTypes = ModifiableValueTypes.DAMAGE_DECREASE

    @staticmethod
    def from_multiply_value(
        multiply_value: DamageMultiplyValue,
    ) -> "DamageDecreaseValue":
        return DamageDecreaseValue(
            position=multiply_value.position,
            damage_type=multiply_value.damage_type,
            target_position=multiply_value.target_position,
            damage=multiply_value.damage,
            damage_elemental_type=multiply_value.damage_elemental_type,
            damage_from_element_reaction=multiply_value.damage_from_element_reaction,
            cost=multiply_value.cost,
            element_reaction=multiply_value.element_reaction,
            reacted_elements=multiply_value.reacted_elements,
        )

    def apply_shield(
        self,
        shield_usage: int,
        min_damage_to_trigger: int,
        max_in_one_time: int,
        decrease_usage_by_damage: bool,
    ) -> int:
        """
        Apply shield to damage, and return the shield usage after applying.

        Args:
            shield_usage: Current shield usage.
            decrease_usage_by_damage: If True, decrease usage by damage,
                and the following two parameters are ignored.
            min_damage_to_trigger: Minimum damage to trigger shield.
            max_in_one_time: Maximum damage to decrease in one time.
        """
        if shield_usage <= 0:
            # no usage, return
            return shield_usage
        if decrease_usage_by_damage:
            # decrease usage by damage
            decrease = min(shield_usage, self.damage)
            self.damage -= decrease
            shield_usage -= decrease
        else:
            if self.damage < min_damage_to_trigger:
                # damage too small to trigger
                return shield_usage
            decrease = min(max_in_one_time, self.damage)
            self.damage -= decrease
            shield_usage -= 1
        return shield_usage


DamageValue = DamageElementEnhanceValue
FinalDamageValue = DamageDecreaseValue  # alias


class UseCardValue(ModifiableValueBase):
    """
    Value to check whether using card success. If use_card is false, then the
    actions about the card are ignored, but will consume cost.
    """

    type: ModifiableValueTypes = ModifiableValueTypes.USE_CARD
    card: Any
    use_card: bool = True
