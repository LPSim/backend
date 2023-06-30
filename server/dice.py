from typing import Literal
from .consts import DiceColor
from .object_base import ObjectBase, ObjectType


class Dice(ObjectBase):
    """
    Class representing a dice. 
    TODO: is combining all dices into one class a good idea?

    Attributes:
        color (DiceColor): The color of the dice.
    """
    type: Literal[ObjectType.DICE] = ObjectType.DICE
    color: DiceColor

    def __str__(self):
        return str(self.color)

    def __repr__(self):
        return repr(self.color)
