from enum import Enum
from typing import List, Any
from ..utils import BaseModel
from .consts import (
    DieColor, DamageType, DamageElementalType,
    ElementalReactionType, ElementType, ObjectPositionType, SkillType
)
from .struct import ObjectPosition, Cost


class ModifiableValueTypes(str, Enum):
    """
    Enum representing the type of a modifiable value. A modifiable value is a
    value that can be modified by other objects before being used.
    """
    INITIAL_DICE_COLOR = 'INITIAL_DICE_COLOR'
    REROLL = 'REROLL'
    COMBAT_ACTION = 'COMBAT_ACTION'
    COST = 'COST'

    # damage calculation is split into 4 parts: increase, multiply and 
    # decrease. damage will be first increased, then multiplied, 
    # then decreased.
    DAMAGE_ELEMENT_ENHANCE = 'DAMAGE_ELEMENT_ENHANCE'
    DAMAGE_INCREASE = 'DAMAGE_INCREASE'
    DAMAGE_MULTIPLY = 'DAMAGE_MULTIPLY'
    DAMAGE_DECREASE = 'DAMAGE_DECREASE'


class ModifiableValueBase(BaseModel):
    """
    Base class of modifiable values. It saves the value and can pass through
    value modifiers to update its value in-place.
    """
    type: ModifiableValueTypes
    original_value: Any = None
    position: ObjectPosition

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        self.original_value = None
        self.original_value = self.copy(deep = True)


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
        self.cost = self.cost.copy(deep = True)
        self.original_value.cost = self.original_value.cost.copy(deep = True)
        self.original_value.cost.original_value = None
        self.cost.original_value = self.original_value.cost.copy(deep = True)


class CombatActionValue(ModifiableValueBase):
    type: ModifiableValueTypes = ModifiableValueTypes.COMBAT_ACTION
    action_label: int
    do_combat_action: bool


class DamageElementEnhanceValue(ModifiableValueBase):
    """
    It describes a detailed damage, i.e. charactor X will receive the damage.
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
            assert self.damage < 0, 'Heal should be negative'
        elif self.damage_type == DamageType.DAMAGE:
            assert self.damage >= 0, 'Damage should be non-negative'
        else:
            assert self.damage_type == DamageType.ELEMENT_APPLICATION
            assert self.damage == 0, 'Element application should be 0'

    def is_corresponding_charactor_use_damage_skill(
        self,
        object_position: ObjectPosition,
        match: Any,
        skill_type: SkillType | None
    ) -> bool:
        """
        Most objects modifying damage when current charactor
        makes damages by using skills. This function checks if the object
        with given object_position is the corresponding charactor using skill.

        If object position is on certain charactor, i.e. equipments or 
        charactor status, the charactor should match damage source. Otherwise,
        the active charactor should be the damage source.

        Args:
            object_position: The position of the object to check.
            match: The match object.
            skill_type: If not None, the skill type should match.
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
            object_position.area == ObjectPositionType.CHARACTOR
            or object_position.area == ObjectPositionType.CHARACTOR_STATUS
        ):
            # object on charactor, get idx
            charactor_idx = object_position.charactor_idx
        else:
            # not on charactor, get active charactor idx
            charactor_idx = match.player_tables[
                object_position.player_idx].active_charactor_idx
        if self.position.charactor_idx != charactor_idx:
            # not same charactor
            return False
        if skill_type is not None:
            skill = match.get_object(self.position)
            if skill.skill_type != skill_type:
                # skill type not match
                return False
        return True

    def is_corresponding_charactor_receive_damage(
        self,
        object_position: ObjectPosition,
        match: Any,
        ignore_piercing: bool = True
    ) -> bool:
        """
        Most objects modifing damage only when current charactor
        receives damages. This function checks if the object with given
        object_position is the corresponding charactor receiving damage.

        If object position is on certain charactor, i.e. equipments or 
        charactor status, the charactor should match damage target. Otherwise,
        the active charactor should be the damage target.

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
            self.target_position.area != ObjectPositionType.CHARACTOR
        ):  # pragma: no cover
            # not on charactor
            return False
        if self.target_position.player_idx != object_position.player_idx:
            # not same player
            return False
        if (
            object_position.area == ObjectPositionType.CHARACTOR
            or object_position.area == ObjectPositionType.CHARACTOR_STATUS
        ):
            # object on charactor, get idx
            charactor_idx = object_position.charactor_idx
        else:
            # not on charactor, get active charactor idx
            charactor_idx = match.player_tables[
                object_position.player_idx].active_charactor_idx
        if self.target_position.charactor_idx != charactor_idx:
            # not same charactor
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
    ) -> 'DamageIncreaseValue':
        return DamageIncreaseValue(
            position = value.position,
            damage_type = value.damage_type,
            target_position = value.target_position,
            damage = value.damage,
            damage_elemental_type = value.damage_elemental_type,
            cost = value.cost,
            damage_from_element_reaction = value.damage_from_element_reaction,
            element_reaction = element_reaction,
            reacted_elements = reacted_elements,
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
        increase_value: DamageIncreaseValue
    ) -> 'DamageMultiplyValue':
        return DamageMultiplyValue(
            position = increase_value.position,
            damage_type = increase_value.damage_type,
            target_position = increase_value.target_position,
            damage = increase_value.damage,
            damage_elemental_type = increase_value.damage_elemental_type,
            damage_from_element_reaction = 
            increase_value.damage_from_element_reaction,
            cost = increase_value.cost,
            element_reaction = increase_value.element_reaction,
            reacted_elements = increase_value.reacted_elements,
        )


class DamageDecreaseValue(DamageIncreaseValue):
    """
    In this stage, damage multiply has been decided, and all decrease-type
    buffs will modify the damage, i.e. various types of shields.
    """
    type: ModifiableValueTypes = ModifiableValueTypes.DAMAGE_DECREASE

    @staticmethod
    def from_multiply_value(
        multiply_value: DamageMultiplyValue
    ) -> 'DamageDecreaseValue':
        return DamageDecreaseValue(
            position = multiply_value.position,
            damage_type = multiply_value.damage_type,
            target_position = multiply_value.target_position,
            damage = multiply_value.damage,
            damage_elemental_type = multiply_value.damage_elemental_type,
            damage_from_element_reaction = 
            multiply_value.damage_from_element_reaction,
            cost = multiply_value.cost,
            element_reaction = multiply_value.element_reaction,
            reacted_elements = multiply_value.reacted_elements,
        )

    def apply_shield(
        self, shield_usage: int, min_damage_to_trigger: int, 
        max_in_one_time: int, decrease_usage_by_damage: bool
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
