from typing import List, Literal

from ....utils.class_registry import register_class

from .eula_3_8 import Eula_3_8 as E_3_8
from .eula_3_8 import IcetideVortex as IV_3_8
from .eula_3_8 import GlacialIllumination as GI_3_8
from .eula_3_8 import LightfallSword_3_8 as LS_3_8
from .eula_3_8 import FavoniusBladeworkEdel


class LightfallSword_3_5(LS_3_8):
    version: Literal['3.5'] = '3.5'
    damage: int = 2


class IcetideVortex(IV_3_8):
    version: Literal['3.5'] = '3.5'


class GlacialIllumination(GI_3_8):
    version: Literal['3.5'] = '3.5'


class Eula_3_5(E_3_8):
    version: Literal['3.5']
    skills: List[
        FavoniusBladeworkEdel | IcetideVortex | GlacialIllumination] = []

    def _init_skills(self) -> None:
        self.skills = [
            FavoniusBladeworkEdel(),
            IcetideVortex(),
            GlacialIllumination()
        ]


register_class(Eula_3_5 | LightfallSword_3_5)
