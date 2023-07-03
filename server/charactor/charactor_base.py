from typing import Literal
from ..object_base import ObjectBase, ObjectType
from ..consts import ElementType


class CharactorBase(ObjectBase):
    name: str
    type: Literal[ObjectType.CHARACTOR] = ObjectType.CHARACTOR
    element: ElementType
    hp: int
    max_hp: int

    @property
    def is_defeated(self):
        return self.hp == 0
