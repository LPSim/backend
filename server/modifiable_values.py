from enum import Enum
from typing import List, Any
from utils import BaseModel
from .consts import (
    DieColor, DamageType, DamageElementalType, DamageSourceType,
    ElementalReactionType, ElementType
)
from .struct import DamageValue, ObjectPosition, DiceCost


class ModifiableValueTypes(str, Enum):
    """
    Enum representing the type of a modifiable value. A modifiable value is a
    value that can be modified by other objects before being used.
    """
    INITIAL_DICE_COLOR = 'INITIAL_DICE_COLOR'
    REROLL = 'REROLL'
    DICE_COST = 'DICE_COST'

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
    value modifiers to update their values.

    TODO: use modify rule lists and apply? especially for damage. And how
    to update inner state when using rule lists?
    """
    type: ModifiableValueTypes
    original_value: Any = None
    match: Any
    position: ObjectPosition
    id: int

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        self.original_value = None
        self.original_value = self.copy()


class InitialDiceColorValue(ModifiableValueBase):
    type: ModifiableValueTypes = ModifiableValueTypes.INITIAL_DICE_COLOR
    player_id: int
    dice_colors: List[DieColor] = []


class RerollValue(ModifiableValueBase):
    type: ModifiableValueTypes = ModifiableValueTypes.REROLL
    value: int
    player_id: int


class DiceCostValue(ModifiableValueBase):
    type: ModifiableValueTypes = ModifiableValueTypes.DICE_COST
    cost: DiceCost

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        self.cost = self.cost.copy()
        self.original_value.cost = self.original_value.cost.copy()
        self.original_value.cost.original_value = None
        self.cost.original_value = self.original_value.cost.copy()


class DamageIncreaseValue(ModifiableValueBase):
    """
    It describes a detailed damage, i.e. charactor X will receive the damage.
    """
    type: ModifiableValueTypes = ModifiableValueTypes.DAMAGE_INCREASE

    damage_type: DamageType
    damage_source_type: DamageSourceType
    target_player_id: int
    target_charactor_id: int
    damage: int
    damage_elemental_type: DamageElementalType
    charge_cost: int
    element_reaction: ElementalReactionType = ElementalReactionType.NONE
    reacted_elements: List[ElementType] = []

    @staticmethod
    def from_damage_value(
        damage_value: DamageValue,
        is_charactors_defeated: List[List[bool]],
        active_charactors_id: List[int],
        match: Any,
        position: ObjectPosition,
        id: int,
    ) -> List['DamageIncreaseValue']:
        """
        use this to identify the real target player and charactor. One 
        DamageValue may generate multiple DamageIncreaseValue (back attack)
        is_charactors_defeated: [[player 1 charactors defeated],
                                 [player 2 charactors defeated]]
        # TODO: need test
        """
        target_player = damage_value.player_id
        if damage_value.target_player == 'ENEMY':
            target_player = 1 - target_player
        charactors = is_charactors_defeated[target_player]
        active_id = active_charactors_id[target_player]
        target_charactor = []
        if damage_value.target_charactor == 'ACTIVE':
            assert not charactors[active_id], 'Active charactor is defeated.'
            target_charactor = [active_id]
        if damage_value.target_charactor == 'BACK':
            target_charactor = [x for x in range(len(charactors))
                                if not charactors[x] and x != active_id]
        elif damage_value.target_charactor == 'NEXT':
            for i in range(1, len(charactors)):
                if not charactors[(active_id + i) % len(charactors)]:
                    target_charactor.append((active_id + i) % len(charactors))
                    break
        elif damage_value.target_charactor == 'PREV':
            for i in range(1, len(charactors)):
                idx = (active_id - i + len(charactors)) % len(charactors)
                if not charactors[idx]:
                    target_charactor.append(idx)
                    break
        result: List[DamageIncreaseValue] = []
        for target in target_charactor:
            assert not charactors[target], 'Target charactor is defeated.'
            value = DamageIncreaseValue(
                match = match,
                position = position,
                id = id,
                damage_type = damage_value.damage_type,
                damage_source_type = damage_value.damage_source_type,
                target_player_id = target_player,
                target_charactor_id = target,
                damage = damage_value.damage,
                damage_elemental_type = damage_value.damage_elemental_type,
                charge_cost = damage_value.charge_cost,
            )
            result.append(value)
        return result


class DamageMultiplyValue(DamageIncreaseValue):
    type: ModifiableValueTypes = ModifiableValueTypes.DAMAGE_MULTIPLY

    @staticmethod
    def from_increase_value(
        increase_value: DamageIncreaseValue
    ) -> 'DamageMultiplyValue':
        return DamageMultiplyValue(
            match = increase_value.match,
            position = increase_value.position,
            id = increase_value.id,
            damage_type = increase_value.damage_type,
            damage_source_type = increase_value.damage_source_type,
            target_player_id = increase_value.target_player_id,
            target_charactor_id = increase_value.target_charactor_id,
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
            match = multiply_value.match,
            position = multiply_value.position,
            id = multiply_value.id,
            damage_type = multiply_value.damage_type,
            damage_source_type = multiply_value.damage_source_type,
            target_player_id = multiply_value.target_player_id,
            target_charactor_id = multiply_value.target_charactor_id,
            damage = multiply_value.damage,
            damage_elemental_type = multiply_value.damage_elemental_type,
            charge_cost = multiply_value.charge_cost,
            element_reaction = multiply_value.element_reaction,
            reacted_elements = multiply_value.reacted_elements,
        )


FinalDamageValue = DamageDecreaseValue  # alias
