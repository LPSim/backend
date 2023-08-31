from enum import Enum
from typing import List, Any, Literal
from utils import BaseModel
from .consts import (
    DieColor, DamageType, DamageElementalType,
    ElementalReactionType, ElementType
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

    # declare a damage. When processing damage, the damage will be change to
    # a damage increase value, based on the declaration and current charactor
    # status.
    DAMAGE = 'DAMAGE'
    # damage calculation is split into 3 parts: increase, multiply and 
    # decrease. damage will be first increased, then multiplied, 
    # then decreased.
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
    cost: Cost

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        self.cost = self.cost.copy(deep = True)
        self.original_value.cost = self.original_value.cost.copy(deep = True)
        self.original_value.cost.original_value = None
        self.cost.original_value = self.original_value.cost.copy(deep = True)


class CombatActionValue(ModifiableValueBase):
    type: ModifiableValueTypes = ModifiableValueTypes.COMBAT_ACTION
    action_type: Literal['SKILL', 'SWITCH', 'END']
    do_combat_action: bool = True


class DamageIncreaseValue(ModifiableValueBase):
    """
    It describes a detailed damage, i.e. charactor X will receive the damage.
    """
    type: ModifiableValueTypes = ModifiableValueTypes.DAMAGE_INCREASE

    damage_type: DamageType
    target_position: ObjectPosition
    damage: int
    damage_elemental_type: DamageElementalType
    charge_cost: int
    element_reaction: ElementalReactionType = ElementalReactionType.NONE
    reacted_elements: List[ElementType] = []


class DamageMultiplyValue(DamageIncreaseValue):
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
            charge_cost = increase_value.charge_cost,
            element_reaction = increase_value.element_reaction,
            reacted_elements = increase_value.reacted_elements,
        )


class DamageDecreaseValue(DamageIncreaseValue):
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
            charge_cost = multiply_value.charge_cost,
            element_reaction = multiply_value.element_reaction,
            reacted_elements = multiply_value.reacted_elements,
        )


DamageValue = DamageIncreaseValue
FinalDamageValue = DamageDecreaseValue  # alias
