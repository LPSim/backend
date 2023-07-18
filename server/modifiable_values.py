from enum import Enum
from typing import List, Any
from utils import BaseModel
from .consts import DieColor


class ModifiableValueTypes(str, Enum):
    """
    Enum representing the type of a modifiable value. A modifiable value is a
    value that can be modified by other objects before being used.
    """
    REROLL = 'REROLL'
    DICECOST = 'DICECOST'

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

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        self.original_value = self.copy()


class RerollValue(ModifiableValueBase):
    type: ModifiableValueTypes = ModifiableValueTypes.REROLL
    value: int
    player_id: int


class DiceCostValue(ModifiableValueBase):
    type: ModifiableValueTypes = ModifiableValueTypes.DICECOST
    elemental_dice_number: int = 0
    elemental_dice_color: DieColor | None = None
    same_dice_number: int = 0
    any_dice_number: int = 0
    omni_dice_number: int = 0

    def is_valid(self, dice_colors: List[DieColor], strict = True) -> bool:
        """
        Check if dice colors matches the dice cost value.
        TODO: test in strict and unstrict mode.

        Args:
            dice_colors (List[DieColor]): The dice colors to be checked.
            strict (bool): If True, the dice colors must match the dice cost
                value strictly. If False, the dice colors can be more than the
                cost.
        """
        assert self.omni_dice_number == 0, 'Omni dice is not supported yet.'
        if self.same_dice_number > 0:
            assert self.elemental_dice_number == 0 and \
                self.any_dice_number == 0, \
                'Same dice and elemental/any dice cannot be both used now.'
        assert not (self.elemental_dice_number > 0 
                    and self.elemental_dice_color is None), \
            'Elemental dice number and color should be both set.'
        if strict:
            if len(dice_colors) != (
                self.elemental_dice_number + self.same_dice_number
                + self.any_dice_number + self.omni_dice_number
            ):
                return False  # dice number not match
        else:
            if len(dice_colors) < (
                self.elemental_dice_number + self.same_dice_number
                + self.any_dice_number + self.omni_dice_number
            ):
                return False  # dice number not enough
        d = {}
        for color in dice_colors:
            d[color] = d.get(color, 0) + 1
        omni_num = d.get(DieColor.OMNI, 0)
        if self.elemental_dice_number > 0:
            ele_num = d.get(self.elemental_dice_color, 0)
            if ele_num + omni_num < self.elemental_dice_number:
                return False  # elemental dice not enough
        if self.same_dice_number > 0:
            for color, same_num in d.items():
                if color == DieColor.OMNI:
                    continue
                if same_num + omni_num < self.same_dice_number:
                    return False  # same dice not enough
        return True
