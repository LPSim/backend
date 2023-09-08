from typing import List, Literal

from ..pyro.xiangling import Xiangling as X_3_8
from ..pyro.xiangling import Pyronado as P_3_8
from ..pyro.xiangling import DoughFu, GuobaAttack


class Pyronado(P_3_8):
    desc: str = '''Deals 2 Pyro DMG, creates 1 Pyronado.'''
    damage: int = 2


class Xiangling_3_3(X_3_8):
    version: Literal['3.3']
    skills: List[DoughFu | GuobaAttack | Pyronado] = []

    def _init_skills(self) -> None:
        self.skills = [
            DoughFu(),
            GuobaAttack(),
            Pyronado()
        ]
