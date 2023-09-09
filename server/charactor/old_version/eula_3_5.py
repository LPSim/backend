from typing import List, Literal

from ..cryo.eula import Eula as E_3_8
from ..cryo.eula import IcetideVortex as IV_3_8
from ..cryo.eula import GlacialIllumination as GI_3_8
from ..cryo.eula import LightfallSword as LS_3_8
from ..cryo.eula import FavoniusBladeworkEdel


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
