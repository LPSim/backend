from enum import Enum
from utils import BaseModel


class ModifiableValueTypes(Enum):
    """
    Enum representing the type of a modifiable value. A modifiable value is a
    value that can be modified by other objects before being used.
    """
    REROLL = 'REROLL'
    DAMAGE = 'DAMAGE'
    COST = 'COST'


class ModifiableValueBase(BaseModel):
    """
    Base class of modifiable values. It saves the value and can pass through
    value modifiers to update their values.
    """
    type: ModifiableValueTypes


class RerollValue(ModifiableValueBase):
    type: ModifiableValueTypes = ModifiableValueTypes.REROLL
    value: int


class ModifiableValueArgumentBase(BaseModel):
    """
    Base class of arguments for modifying values. It will be passed to the
    value modifiers together with the value to be modified, and modifiers 
    can decide how to modify the value based on the arguments.
    """
    type: ModifiableValueTypes


class RerollValueArguments(ModifiableValueArgumentBase):
    """
    Arguments for modifying reroll value.

    Args:
        player_id (int): The ID of the player who is triggering the value
            modifier.
    """
    type: ModifiableValueTypes = ModifiableValueTypes.REROLL
    player_id: int


ModifiableValues = ModifiableValueBase | RerollValue
ModifiableValueArguments = ModifiableValueArgumentBase | RerollValueArguments
