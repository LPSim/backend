from typing import Literal
from .cryo_charactors import Grimheart as G_3_8


class Grimheart(G_3_8):
    version: Literal['3.5'] = '3.5'
    damage: int = 2


OldVersionCharactorStatus = Grimheart | Grimheart
