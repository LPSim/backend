from typing import Literal
from .cryo_charactors import Grimheart as G_3_8
from .foods import MintyMeatRolls as MMR_3_4


class Grimheart_3_5(G_3_8):
    version: Literal['3.5']
    damage: int = 2


class MintyMeatRolls_3_3(MMR_3_4):
    desc: str = (
        "During this Round, the target character's Normal Attacks cost "
        "less 1 Unaligned Element."
    )
    version: Literal['3.3']
    decrease_usage: int = 999


OldVersionCharactorStatus = Grimheart_3_5 | MintyMeatRolls_3_3
