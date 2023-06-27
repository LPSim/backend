from typing import Literal
from server.object_base import ObjectBase


class CharactorBase(ObjectBase):
    name: Literal['CharactorBase'] = 'CharactorBase'
