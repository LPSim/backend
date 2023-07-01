from typing import Literal
from .consts import DieColor
from .object_base import ObjectBase, ObjectType


class Die(ObjectBase):
    """
    Class representing a die. 
    TODO: is combining all dice into one class a good idea?

    Attributes:
        color (DiceColor): The color of the dice.
    """
    type: Literal[ObjectType.DIE] = ObjectType.DIE
    color: DieColor

    def __str__(self):
        return str(self.color)

    def __repr__(self):
        return repr(self.color)
