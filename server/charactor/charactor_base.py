from typing import Literal
from ..object_base import ObjectBase
from ..consts import ElementType


class CharactorBase(ObjectBase):
    name: Literal['CharactorBase'] = 'CharactorBase'
    element: ElementType
